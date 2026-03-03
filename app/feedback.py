import re


def analyze(transcript: str) -> dict:
    """Returns feedback such as repeated words, grammar issues, english level."""
    words = re.findall(r"\w+", transcript.lower())
    repeats = {w: words.count(w) for w in set(words) if words.count(w) > 2}
    # naive grammar check placeholder
    grammar_issues = []
    if " i " in transcript:
        grammar_issues.append("Consider capitalizing 'I'")
    return {
        "repeated_words": repeats,
        "grammar_issues": grammar_issues,
    }
