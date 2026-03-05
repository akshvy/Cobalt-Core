from app.resume_parser import parse_resume, extract_text


def test_parse_sections():
    text = "Education:\nBSc in Computer Science, MIT 2018\nExperience:\n3 years at Acme as Backend Engineer"
    data = parse_resume(text)
    assert 'education' in data
    assert 'experience' in data


def test_parse_email():
    text = "John Doe\njohn.doe@example.com\nSkills: Python, Go"
    data = parse_resume(text)
    assert 'email' in data
    assert data['email'] == 'john.doe@example.com'


def test_parse_no_sections():
    text = "Just a plain block of text with no recognisable sections."
    data = parse_resume(text)
    # Should not crash and should return a dict
    assert isinstance(data, dict)


def test_extract_text_plain():
    content = b"Hello\nWorld\nThis is a resume."
    text = extract_text(content, "resume.txt")
    assert "Hello" in text
    assert "resume" in text
