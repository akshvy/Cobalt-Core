from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import resume_parser, interviewer, feedback
import json

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

@app.post("/start_interview")
def start_interview(payload: dict):
    role = payload.get('role')
    resume_data = payload.get('resume_data')
    question = interviewer.next_question(role, resume_data)
    return {"question": question}

@app.post("/submit_answer")
def submit_answer(payload: dict):
    answer = payload.get('answer')
    history = payload.get('history', [])
    # history is list of {question, answer} pairs
    result = interviewer.evaluate_answer(answer, history)
    return result

@app.post("/feedback")
def get_feedback(payload: dict):
    transcript = payload.get('transcript', '')
    return feedback.analyze(transcript)


@app.post("/video_audio")
async def video_audio(file: UploadFile = File(...), history: str = Form("[]")):
    # history is a JSON-encoded list of question/answer dicts
    bytes_data = await file.read()
    try:
        hist = json.loads(history)
    except Exception:
        hist = []
    result = interviewer.transcribe_and_evaluate(bytes_data, hist)
    return result
