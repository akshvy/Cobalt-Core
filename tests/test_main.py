from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


def test_upload_resume_text():
    # send a plain text resume
    data = {
        'file': ('resume.txt', io.BytesIO(b"Education\nExperience"), 'text/plain')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 200
    json_data = res.json()
    assert 'parsed' in json_data
    assert isinstance(json_data['parsed'], dict)


def test_upload_resume_bad_type():
    data = {
        'file': ('image.png', io.BytesIO(b"not a pdf"), 'image/png')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 400
    assert 'Unsupported file type' in res.json()['detail']


def test_upload_resume_empty_pdf(monkeypatch):
    # simulate a pdf that extracts no text
    def fake_extract_text(raw_bytes, filename):
        return ""  # no text

    monkeypatch.setattr('app.resume_parser.extract_text', fake_extract_text)
    data = {
        'file': ('empty.pdf', io.BytesIO(b"dummy"), 'application/pdf')
    }
    res = client.post('/upload_resume', files=data)
    assert res.status_code == 500
    assert 'No text extracted' in res.json()['detail']


def test_video_audio_no_history():
    # send a mock audio blob and ensure the endpoint returns transcript key
    blob = io.BytesIO(b"dummy audio")
    res = client.post('/video_audio', files={'file': ('a.webm', blob, 'audio/webm')})
    assert res.status_code == 200
    json_data = res.json()
    assert 'transcript' in json_data
    assert 'evaluation' in json_data
