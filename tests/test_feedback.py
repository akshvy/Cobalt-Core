from app.feedback import analyze


def test_analyze_repeated_words():
    transcript = "hello hello hello world world world"
    result = analyze(transcript)
    assert 'repeated_words' in result
    # "hello" and "world" each appear 3 times
    assert result['repeated_words'].get('hello') == 3
    assert result['repeated_words'].get('world') == 3


def test_analyze_grammar_lowercase_i():
    transcript = "this is me i am here and i will do it"
    result = analyze(transcript)
    assert 'grammar_issues' in result
    assert any("Capitalise" in issue or "capitaliz" in issue.lower() for issue in result['grammar_issues'])


def test_analyze_filler_words():
    transcript = "um like I basically um sort of did it"
    result = analyze(transcript)
    assert 'filler_words' in result
    assert 'um' in result['filler_words']
    assert result['filler_words']['um'] == 2


def test_vocabulary_score_range():
    transcript = "The quick brown fox jumps over the lazy dog"
    result = analyze(transcript)
    assert 0 <= result['vocabulary_score'] <= 100


def test_clarity_score_range():
    transcript = "I built a scalable REST API using Python and FastAPI."
    result = analyze(transcript)
    assert 0 <= result['clarity_score'] <= 100


def test_short_transcript():
    result = analyze("Yes.")
    assert result['total_words'] == 1
    assert result['vocabulary_score'] == 100.0
