from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import resume_parser, interviewer, feedback, models
import json

# initialize database
models.init_db()

app = FastAPI(
    title="Cobalt Core AI Interviewer",
    description="An intelligent mock interview platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = await file.read()
    text = resume_parser.extract_text(content, file.filename)
    data = resume_parser.parse_resume(text)
    return {"parsed": data}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/start_interview")
def start_interview(payload: dict, db: Session = Depends(get_db)):
    role = payload.get('role')
    resume_data = payload.get('resume_data')
    # create persistent session
    sess = models.InterviewSession(role=role, resume_data=resume_data)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    question = interviewer.next_question(role, resume_data, [])
    return {"session_id": sess.id, "question": question}

@app.post("/submit_answer")
def submit_answer(payload: dict, db: Session = Depends(get_db)):
    session_id = payload.get('session_id')
    answer = payload.get('answer')
    history = payload.get('history', [])
    # record entry if session exists
    if session_id is not None:
        qa = models.QAEntry(session_id=session_id, question=history[-1].get('question') if history else None, answer=answer)
        db.add(qa)
        db.commit()
    result = interviewer.evaluate_answer(answer, history)
    return result

@app.post("/feedback")
def get_feedback(payload: dict):
    transcript = payload.get('transcript', '')
    return feedback.analyze(transcript)


@app.post("/video_audio")
async def video_audio(file: UploadFile = File(...), history: str = Form("[]"), session_id: int = Form(None), db: Session = Depends(get_db)):
    # history is a JSON-encoded list of question/answer dicts
    bytes_data = await file.read()
    try:
        hist = json.loads(history)
    except Exception:
        hist = []
    result = interviewer.transcribe_and_evaluate(bytes_data, hist)
    # optionally store as QA entry
    if session_id is not None:
        transcription = result.get('transcript')
        qa = models.QAEntry(session_id=session_id, question=hist[-1].get('question') if hist else None, answer=transcription)
        db.add(qa)
        db.commit()
    return result
