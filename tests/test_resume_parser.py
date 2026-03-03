from app.resume_parser import parse_resume

def test_parse_sections():
    text = "Education:\nBSc in CS\nExperience:\n2 years at X"
    data = parse_resume(text)
    assert 'education' in data
    assert 'experience' in data
