from typing import List, Dict, Optional
import io
import re
from .config import settings

# ---------------------------------------------------------------------------
# Helper: get an OpenAI client only when a key is available
# ---------------------------------------------------------------------------

def _client():
    """Return an openai.OpenAI client, or None if no API key is set."""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Fallback question bank used when OpenAI is unavailable
# ---------------------------------------------------------------------------

FALLBACK_QUESTIONS = [
    "Can you walk me through your most recent project and the technical decisions you made?",
    "How do you approach debugging a complex issue in production?",
    "Describe a time you had to learn a new technology quickly. How did you handle it?",
    "What strategies do you use to ensure code quality and maintainability?",
    "Tell me about a situation where you had to collaborate with a difficult stakeholder.",
    "How do you prioritise tasks when facing multiple deadlines?",
    "What does a good code review process look like to you?",
    "Describe a technical challenge you faced and how you overcame it.",
]

_question_index = 0


def _fallback_question() -> str:
    global _question_index
    q = FALLBACK_QUESTIONS[_question_index % len(FALLBACK_QUESTIONS)]
    _question_index += 1
    return q


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def next_question(role: str, resume_data: dict, history: List[Dict]) -> str:
    """Generate a contextual interview question. Falls back gracefully."""
    client = _client()
    if client is None:
        return _fallback_question()

    try:
        history_str = "\n".join(
            f"Q: {h.get('question', '')}\nA: {h.get('answer', '')}"
            for h in history[-3:]
        ) or "No previous questions."

        resume_str = str(resume_data) if resume_data else "No resume provided."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an experienced technical interviewer. "
                    "Ask one clear, specific interview question relevant to the candidate's background. "
                    "Do NOT include any preamble — output only the question."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Role: {role}\n"
                    f"Resume highlights: {resume_str}\n"
                    f"Recent conversation:\n{history_str}\n\n"
                    "Ask the next interview question."
                ),
            },
        ]

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=120,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Tell me about a challenging project you worked on. (Note: AI question generation error: {e})"


def evaluate_answer(answer: str, history: List[Dict]) -> dict:
    """Evaluate a candidate's answer. Returns score + feedback."""
    if not answer or not answer.strip():
        return {"score": 0, "feedback": "No answer provided.", "strengths": [], "improvements": ["Please provide a detailed answer."]}

    client = _client()
    if client is None:
        # Simple heuristic fallback
        word_count = len(answer.split())
        score = min(10, max(1, word_count // 10))
        feedback = (
            "Good detail! Try to add specific examples." if word_count > 30
            else "Try to elaborate more — aim for at least 3-4 sentences."
        )
        return {"score": score, "feedback": feedback, "strengths": [], "improvements": []}

    try:
        history_str = "\n".join(
            f"Q: {h.get('question', '')}\nA: {h.get('answer', '')}"
            for h in history[-2:]
        ) or "None"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an experienced interview coach. "
                    "Evaluate the candidate's answer and respond in this exact JSON format:\n"
                    '{"score": <1-10>, "feedback": "<overall assessment>", '
                    '"strengths": ["<strength1>", ...], "improvements": ["<area1>", ...]}\n'
                    "Be concise. Output valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Previous conversation:\n{history_str}\n\n"
                    f"Candidate's answer:\n{answer}\n\n"
                    "Evaluate this answer."
                ),
            },
        ]

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content.strip()

        import json
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        return {
            "score": data.get("score"),
            "feedback": data.get("feedback", ""),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
        }
    except Exception as e:
        word_count = len(answer.split())
        score = min(10, max(1, word_count // 10))
        return {
            "score": score,
            "feedback": f"Answer received. (AI evaluation unavailable: {e})",
            "strengths": [],
            "improvements": [],
        }


def transcribe_and_evaluate(audio_bytes: bytes, history: List[Dict]) -> dict:
    """Transcribe audio with Whisper then evaluate the answer."""
    client = _client()

    transcription = ""
    if client is None:
        transcription = "[Transcription unavailable — OpenAI API key not configured]"
    else:
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            transcription = resp.text
        except Exception as e:
            transcription = f"[Transcription error: {e}]"

    evaluation = evaluate_answer(transcription, history)
    return {"transcript": transcription, "evaluation": evaluation}
