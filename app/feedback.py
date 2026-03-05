import re
from collections import Counter
from .config import settings

# Common filler words in English
FILLER_WORDS = {
    'um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally', 'i mean',
    'sort of', 'kind of', 'well', 'so', 'anyway', 'you see', 'i think', 'obviously',
}


def analyze(transcript: str) -> dict:
    """Returns comprehensive feedback including repeated words, grammar,
    filler words, vocabulary score, and clarity score."""

    words = re.findall(r"\w+", transcript.lower())
    total_words = len(words)
    word_counts = Counter(words)

    # Words appearing more than twice (excluding very common stop words)
    stop_words = {'the', 'a', 'an', 'is', 'it', 'in', 'on', 'at', 'to', 'for',
                  'of', 'and', 'or', 'but', 'not', 'with', 'this', 'that', 'was',
                  'are', 'be', 'been', 'by', 'from', 'as', 'up', 'do', 'did', 'has',
                  'have', 'had', 'my', 'your', 'we', 'i', 'he', 'she', 'they', 'me'}
    repeats = {
        w: c for w, c in word_counts.items()
        if c > 2 and w not in stop_words and len(w) > 2
    }

    # Grammar checks
    grammar_issues = []
    # Lowercase 'i' used alone
    if re.search(r"\bi\b(?!')", transcript):
        grammar_issues.append("Capitalise 'I' when used as a pronoun")
    # your're (typo)
    if re.search(r"\byour're\b", transcript.lower()):
        grammar_issues.append("Did you mean 'you're' (you are)?")
    # double spaces
    if "  " in transcript:
        grammar_issues.append("Extra spaces detected")
    # Common contractions
    for wrong, right in [("cant ", "can't "), ("dont ", "don't "), ("wont ", "won't "), ("didnt ", "didn't ")]:
        if wrong in transcript.lower():
            grammar_issues.append(f"Consider using '{right.strip()}' instead of '{wrong.strip()}'")

    # Filler words
    transcript_lower = transcript.lower()
    filler_count = {}
    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = len(re.findall(pattern, transcript_lower))
        if matches > 0:
            filler_count[filler] = matches

    # Vocabulary diversity score (type-token ratio)
    unique_words = len(set(words))
    vocabulary_score = (unique_words / max(total_words, 1)) * 100

    # Clarity metrics
    sentences = [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]
    avg_sentence_length = total_words / max(len(sentences), 1)
    clarity_score = 100.0
    if avg_sentence_length > 35:
        clarity_score -= 25  # Very long sentences hurt clarity
    elif avg_sentence_length > 25:
        clarity_score -= 10
    if avg_sentence_length < 4:
        clarity_score -= 15  # Very short / fragmented
    if len(filler_count) > 3:
        clarity_score -= 10
    clarity_score = max(0.0, clarity_score)

    # Hesitation markers
    hesitation_count = len(re.findall(r'\.\.\.|!!!|\?\?', transcript))

    # Optional: AI-powered grammar analysis
    ai_text = ""
    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an English tutor who briefly critiques transcripts."},
                    {
                        "role": "user",
                        "content": (
                            "Analyse the following transcript for grammar mistakes and communication quality. "
                            "Give a 2-3 sentence assessment. Be constructive and specific.\n\n"
                            f"Transcript:\n{transcript}"
                        ),
                    },
                ],
                max_tokens=200,
            )
            ai_text = resp.choices[0].message.content.strip()
        except Exception as e:
            ai_text = f"[AI analysis unavailable: {e}]"

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
