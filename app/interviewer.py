from typing import List, Dict
import openai
import io

# stub functions for AI interaction
def next_question(role: str, resume_data: dict) -> str:
    # In a real implementation we would call the AI engine
    # to generate a question based on the role and resume.
    return f"Can you describe your experience relevant to {role}?"


def evaluate_answer(answer: str, history: List[Dict]) -> dict:
    # Dummy evaluation: count words, check for keywords
    score = len(answer.split())
    feedback = "Good" if score > 5 else "Try to elaborate more"
    return {"score": score, "feedback": feedback}


def transcribe_and_evaluate(audio_bytes: bytes, history: List[Dict]):
    """Use OpenAI to transcribe audio then evaluate the text. Returns transcript and evaluation."""
    try:
        audio_file = io.BytesIO(audio_bytes)
        # Whisper API expects a filename attribute on file-like objects
        audio_file.name = "audio.wav"
        resp = openai.Audio.transcribe("whisper-1", audio_file)
        transcription = resp.get("text", "")
    except Exception as e:
        transcription = f"[transcription error: {e}]"
    evaluation = evaluate_answer(transcription, history)
    return {"transcript": transcription, "evaluation": evaluation}
