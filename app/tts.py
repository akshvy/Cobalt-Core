import io
from .config import settings


def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS and return audio bytes."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        raise RuntimeError(f"Text-to-speech error: {e}") from e


def get_ai_response(transcript: str, role: str, history: list = None) -> dict:
    """Generate AI feedback for a candidate's answer and optionally return audio."""
    if history is None:
        history = []

    if not settings.OPENAI_API_KEY:
        return {"response": "API key not configured — please set OPENAI_API_KEY.", "audio": None}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        history_str = "\n".join(
            f"Q: {h.get('question', '')}\nA: {h.get('answer', '')}"
            for h in history[-2:]
        ) or "None"

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an interviewer for a {role} position. "
                    "Give brief, constructive feedback on the candidate's answer, "
                    "then ask a follow-up question. Keep it to 2 sentences total."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Previous Q&A:\n{history_str}\n\n"
                    f"Candidate just said: {transcript}\n\n"
                    "Respond with feedback and your next question."
                ),
            },
        ]

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.6,
        )
        response_text = resp.choices[0].message.content.strip()

        try:
            audio_bytes = text_to_speech(response_text)
            audio_hex = audio_bytes.hex()
        except Exception:
            audio_hex = None

        return {"response": response_text, "audio": audio_hex}

    except Exception as e:
        return {"response": f"Error generating response: {e}", "audio": None}
