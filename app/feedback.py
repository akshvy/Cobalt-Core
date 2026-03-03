import re
import openai
from collections import Counter
from .config import settings

openai.api_key = settings.OPENAI_API_KEY

# Common filler words in English
FILLER_WORDS = {
    'um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally', 'i mean',
    'sort of', 'kind of', 'well', 'so', 'anyway', 'you see', 'i think', 'obviously'
}

def analyze(transcript: str) -> dict:
    """Returns comprehensive feedback including repeated words, grammar, filler words, vocabulary, and clarity."""
    words = re.findall(r"\w+", transcript.lower())
    repeats = {w: words.count(w) for w in set(words) if words.count(w) > 2}
    
    grammar_issues = []
    if " i " in transcript.lower():
        grammar_issues.append("Consider capitalizing 'I'")
    if re.search(r"\byour're\b", transcript.lower()):
        grammar_issues.append("Did you mean 'you are'?")
    
    # Filler words analysis
    transcript_lower = transcript.lower()
    filler_count = {}
    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = len(re.findall(pattern, transcript_lower))
        if matches > 0:
            filler_count[filler] = matches
    
    # Vocabulary diversity
    unique_words = len(set(words))
    total_words = len(words)
    vocabulary_score = (unique_words / max(total_words, 1)) * 100
    
    # Clarity metrics
    sentences = re.split(r'[.!?]+', transcript)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_length = total_words / max(len(sentences), 1)
    clarity_score = 100.0
    if avg_sentence_length > 30:
        clarity_score -= 20
    if avg_sentence_length < 5:
        clarity_score -= 10
    
    hesitation_count = len(re.findall(r'\.\.\.|!!!|\?\?', transcript))

    ai_text = ""
    if settings.OPENAI_API_KEY:
        try:
            system_msg = "You are an English tutor who critiques transcripts."
            user_prompt = (
                f"Please analyze the following transcript for grammar mistakes, "
                "usage issues, and give a short assessment of the speaker's "
                "English proficiency level (e.g., beginner, intermediate, advanced). "
                f"Transcript:\n{transcript}"
            )
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=300,
            )
            ai_text = resp.choices[0].message.content.strip()
        except Exception as e:
            ai_text = f"[AI analysis error: {e}]"

    return {
        "repeated_words": repeats,
        "grammar_issues": grammar_issues,
        "filler_words": filler_count,
        "vocabulary_score": round(vocabulary_score, 2),
        "clarity_score": round(clarity_score, 2),
        "hesitation_score": hesitation_count,
        "unique_words": unique_words,
        "total_words": total_words,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "ai_analysis": ai_text,
    }
