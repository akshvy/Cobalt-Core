from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json

from . import resume_parser, interviewer, feedback, tts
from .models import init_db, get_db, InterviewSession, QAEntry

# Initialise database tables on startup
init_db()

app = FastAPI(
    title="Cobalt Core AI Interviewer",
    description="An intelligent mock interview platform",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, TXT, or DOCX file.")

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        text = resume_parser.extract_text(content, file.filename)
        if not text or not text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No text could be extracted from this file. "
                    "If it's a scanned PDF, please export it as a text PDF or upload a .txt / .docx version instead."
                ),
            )
        data = resume_parser.parse_resume(text)
        # Also pass the raw text so question generation has full context
        data["raw_text"] = text[:3000]  # cap to avoid huge payloads
        return {"parsed": data, "text_preview": text[:500]}
    except HTTPException:
        raise
    except RuntimeError as e:
        # Raised by extract_text with a user-friendly message
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing file: {e}")


# ---------------------------------------------------------------------------
# Interview session
# ---------------------------------------------------------------------------

@app.post("/start_interview")
def start_interview(payload: dict, db: Session = Depends(get_db)):
    role = payload.get("role", "Software Engineer")
    resume_data = payload.get("resume_data") or {}

    sess = InterviewSession(role=role, resume_data=resume_data)
    db.add(sess)
    db.commit()
    db.refresh(sess)

    question = interviewer.next_question(role, resume_data, [])
    return {"session_id": sess.id, "question": question}


@app.post("/submit_answer")
def submit_answer(payload: dict, db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    answer = payload.get("answer", "")
    history = payload.get("history", [])

    if not answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    session = None
    if session_id is not None:
        session = db.get(InterviewSession, session_id)

    evaluation = interviewer.evaluate_answer(answer, history)

    if session is not None:
        qa = QAEntry(
            session_id=session_id,
            question=history[-1].get("question") if history else None,
            answer=answer,
            score=float(evaluation.get("score") or 0),
            feedback=evaluation.get("feedback", ""),
        )
        db.add(qa)
        db.commit()

    response = {"evaluation": evaluation}

    if session is not None:
        new_history = history + [
            {"question": history[-1].get("question") if history else None, "answer": answer}
        ]
        response["next_question"] = interviewer.next_question(
            session.role, session.resume_data, new_history
        )

    return response


# ---------------------------------------------------------------------------
# Video / audio
# ---------------------------------------------------------------------------

@app.post("/video_audio")
async def video_audio(
    file: UploadFile = File(...),
    history: str = Form("[]"),
    session_id: str = Form(None),
    db: Session = Depends(get_db),
):
    bytes_data = await file.read()
    try:
        hist = json.loads(history)
    except Exception:
        hist = []

    result = interviewer.transcribe_and_evaluate(bytes_data, hist)

    session = None
    sid = None
    if session_id and session_id.strip() and session_id.strip() != "null":
        try:
            sid = int(session_id)
            session = db.get(InterviewSession, sid)
        except (ValueError, TypeError):
            pass

    if session is not None:
        qa = QAEntry(
            session_id=sid,
            question=hist[-1].get("question") if hist else None,
            answer=result.get("transcript", ""),
            score=float(result.get("evaluation", {}).get("score") or 0),
            feedback=result.get("evaluation", {}).get("feedback", ""),
        )
        db.add(qa)
        db.commit()

    response = {**result}
    if session is not None:
        new_history = hist + [
            {"question": hist[-1].get("question") if hist else None, "answer": result.get("transcript")}
        ]
        response["next_question"] = interviewer.next_question(
            session.role, session.resume_data, new_history
        )
    return response


@app.post("/ai_voice_response")
def ai_voice_response(payload: dict, db: Session = Depends(get_db)):
    transcript = payload.get("transcript", "")
    session_id = payload.get("session_id")
    history = payload.get("history", [])
    role = payload.get("role", "Software Engineer")

    if session_id:
        session = db.get(InterviewSession, session_id)
        if session:
            role = session.role

    return tts.get_ai_response(transcript, role, history)


# ---------------------------------------------------------------------------
# Feedback analysis
# ---------------------------------------------------------------------------

@app.post("/feedback")
def get_feedback(payload: dict):
    transcript = payload.get("transcript", "")
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")
    return feedback.analyze(transcript)


# ---------------------------------------------------------------------------
# Session history
# ---------------------------------------------------------------------------

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = (
        db.query(InterviewSession)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )
    return [
        {"id": s.id, "role": s.role, "started_at": s.started_at.isoformat()}
        for s in sessions
    ]


@app.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    qa_list = (
        db.query(QAEntry)
        .filter(QAEntry.session_id == session_id)
        .order_by(QAEntry.created_at)
        .all()
    )
    interactions = [
        {
            "question": qa.question,
            "answer": qa.answer,
            "score": qa.score,
            "feedback": qa.feedback,
            "created_at": qa.created_at.isoformat(),
        }
        for qa in qa_list
    ]

    return {
        "id": session.id,
        "role": session.role,
        "started_at": session.started_at.isoformat(),
        "interactions": interactions,
    }


@app.post("/end_session")
def end_session(payload: dict, db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    session = db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    qa_list = (
        db.query(QAEntry)
        .filter(QAEntry.session_id == session_id)
        .all()
    )

    scores = [qa.score for qa in qa_list if qa.score and qa.score > 0]
    avg_score = round(sum(scores) / len(scores) * 10, 1) if scores else 0  # scale to 100

    return {
        "session_id": session_id,
        "total_interactions": len(qa_list),
        "final_score": min(100, avg_score),
        "role": session.role,
    }


# ---------------------------------------------------------------------------
# Serve frontend (must be last so API routes take precedence)
# ---------------------------------------------------------------------------
import os
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
