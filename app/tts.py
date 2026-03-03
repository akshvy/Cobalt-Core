import os
from gtts import gTTS
import io
from .config import settings

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using Google TTS and return audio bytes."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        raise Exception(f"Text-to-speech error: {e}")

def get_ai_response(transcript: str, role: str, history: list = None) -> dict:
    """Generate an AI response to a user's answer and convert to speech."""
    if history is None:
        history = []
    
    import openai
    openai.api_key = settings.OPENAI_API_KEY
    
    if not settings.OPENAI_API_KEY:
        return {
            "response": "API key not configured",
            "audio": None
        }
    
    try:
        system_msg = f"You are an interviewer for a {role} position. Provide constructive feedback and ask the next question."
        user_prompt = (
            f"The candidate answered: {transcript}\n"
            f"Previous Q&A:\n" + "\n".join([f"Q: {h.get('question', '')}\nA: {h.get('answer', '')}" for h in history[-2:]]) +
            "\nProvide feedback and ask the next challenging question in 1-2 sentences."
        )
        
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=150,
        )
        
        response_text = resp.choices[0].message.content.strip()
        audio_bytes = text_to_speech(response_text)
        
        return {
            "response": response_text,
            "audio": audio_bytes.hex()  # convert to hex for JSON serialization
        }
    except Exception as e:
        return {
            "response": f"Error generating response: {e}",
            "audio": None
        }
