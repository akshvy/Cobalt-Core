from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


def test_upload_resume_text():
    """Plain text resume should parse successfully."""
    data = {
        'file': ('resume.txt', io.BytesIO(b"Education\nBSc Computer Science\nExperience\n3 years at Acme Corp"), 'text/plain')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 200
    json_data = res.json()
    assert 'parsed' in json_data
    assert isinstance(json_data['parsed'], dict)


def test_upload_resume_bad_type():
    """Image uploads should be rejected with HTTP 400."""
    data = {
        'file': ('image.png', io.BytesIO(b"not a resume"), 'image/png')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 400
    assert 'Unsupported' in res.json()['detail']


def test_upload_resume_empty(monkeypatch):
    """A file that yields no text should return HTTP 500."""
    monkeypatch.setattr('app.resume_parser.extract_text', lambda *_: "")
    data = {
        'file': ('empty.pdf', io.BytesIO(b"dummy"), 'application/pdf')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 500
    assert 'No text' in res.json()['detail']


def test_start_interview_without_resume():
    """start_interview with empty resume_data should still return a question."""
    res = client.post('/start_interview', json={'role': 'Software Engineer', 'resume_data': {}})
    assert res.status_code == 200
    data = res.json()
    assert 'session_id' in data
    assert 'question' in data
    assert isinstance(data['question'], str)
    assert len(data['question']) > 0


def test_submit_answer_empty():
    """Submitting an empty answer should return HTTP 400."""
    res = client.post('/submit_answer', json={'answer': '', 'history': []})
    assert res.status_code == 400


def test_submit_answer_valid():
    """A valid answer should return an evaluation dict."""
    # First create a session
    start = client.post('/start_interview', json={'role': 'Data Scientist', 'resume_data': {}})
    sid = start.json()['session_id']

    res = client.post('/submit_answer', json={
        'session_id': sid,
        'answer': 'I have five years of experience building ML pipelines using Python and TensorFlow.',
        'history': [],
    })
    assert res.status_code == 200
    data = res.json()
    assert 'evaluation' in data
    assert 'feedback' in data['evaluation']


def test_feedback_analysis():
    """Feedback endpoint should return all expected keys."""
    res = client.post('/feedback', json={
        'transcript': 'um like I basically um sort of built a thing you know it was like really good'
    })
    assert res.status_code == 200
    data = res.json()
    assert 'vocabulary_score' in data
    assert 'clarity_score' in data
    assert 'filler_words' in data
    assert 'grammar_issues' in data
    assert 'repeated_words' in data


def test_feedback_empty_transcript():
    """Empty transcript should return HTTP 400."""
    res = client.post('/feedback', json={'transcript': '   '})
    assert res.status_code == 400


def test_video_audio_returns_transcript():
    """video_audio should return a transcript key even without a real audio file."""
    blob = io.BytesIO(b"dummy audio data that wont really transcribe")
    res = client.post('/video_audio', files={'file': ('a.webm', blob, 'audio/webm')})
    assert res.status_code == 200
    data = res.json()
    assert 'transcript' in data
    assert 'evaluation' in data


def test_sessions_list():
    """Sessions list should return a list."""
    res = client.get('/sessions')
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_session_not_found():
    """Requesting a nonexistent session should return 404."""
    res = client.get('/sessions/999999')
    assert res.status_code == 404
