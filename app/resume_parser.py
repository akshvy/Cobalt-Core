import io
import pdfplumber
import docx
import re


def extract_text(raw_bytes: bytes, filename: str) -> str:
    """Extracts text from pdf/docx/plain files."""
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif filename.lower().endswith(".docx"):
        doc = docx.Document(io.BytesIO(raw_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        # assume text
        return raw_bytes.decode(errors="ignore")


def parse_resume(text: str) -> dict:
    """Very naive resume parser that looks for sections and keywords."""
    data = {}
    # split into lines and look for headings
    lines = text.splitlines()
    for line in lines:
        if re.match(r"^education", line, re.I):
            data['education'] = line
        elif re.match(r"^experience", line, re.I):
            data['experience'] = line
    # Could be extended later
    return data
