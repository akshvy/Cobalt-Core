import io
import re


def extract_text(raw_bytes: bytes, filename: str) -> str:
    """Extract text from PDF, DOCX, or plain-text files.

    For PDFs we try three strategies in order:
      1. pdfplumber  – best for text-layer PDFs
      2. pypdf (PyPDF2 successor) – good fallback for some layouts
      3. pdfminer.six – deepest text extraction, handles more edge cases
    We use the result from whichever strategy yields the most text.
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        errors = []
        candidates = []

        # Strategy 1: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    t = page.extract_text(x_tolerance=3, y_tolerance=3)
                    if t:
                        pages_text.append(t)
            text = "\n".join(pages_text).strip()
            if text:
                candidates.append(text)
        except Exception as e:
            errors.append(f"pdfplumber: {e}")

        # Strategy 2: pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text() or ""
                if t.strip():
                    pages_text.append(t)
            text = "\n".join(pages_text).strip()
            if text:
                candidates.append(text)
        except ImportError:
            pass  # pypdf not installed — skip silently
        except Exception as e:
            errors.append(f"pypdf: {e}")

        # Strategy 3: pdfminer
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(io.BytesIO(raw_bytes)) or ""
            text = text.strip()
            if text:
                candidates.append(text)
        except ImportError:
            pass  # pdfminer not installed — skip silently
        except Exception as e:
            errors.append(f"pdfminer: {e}")

        if candidates:
            # Return the longest result (most content extracted)
            return max(candidates, key=len)

        # All strategies failed or returned empty
        err_detail = "; ".join(errors) if errors else "all extraction methods returned empty text"
        raise RuntimeError(
            f"Could not extract text from this PDF ({err_detail}). "
            "This may be a scanned/image-only PDF. "
            "Please try saving it as text or copy-pasting your resume as a .txt file."
        )

    elif name.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(raw_bytes))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            raise RuntimeError(f"Could not read DOCX: {e}") from e

    else:
        # Plain text fallback
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw_bytes.decode(errors="replace")


# Section headings we try to detect
_SECTION_PATTERNS = {
    "name":        re.compile(r"^name[:\s]*(.+)$", re.I),
    "email":       re.compile(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", re.I),
    "phone":       re.compile(r"(\+?\d[\d\s\-().]{7,}\d)", re.I),
    "linkedin":    re.compile(r"linkedin\.com/in/[\w\-]+", re.I),
    "github":      re.compile(r"github\.com/[\w\-]+", re.I),
    "education":   re.compile(r"^education", re.I | re.M),
    "experience":  re.compile(r"^(work\s+)?experience", re.I | re.M),
    "skills":      re.compile(r"^(technical\s+)?skills", re.I | re.M),
    "projects":    re.compile(r"^projects?", re.I | re.M),
    "summary":     re.compile(r"^(summary|objective|profile)", re.I | re.M),
    "certifications": re.compile(r"^certifications?", re.I | re.M),
}


def parse_resume(text: str) -> dict:
    """Extract structured information from resume text."""
    data: dict = {}
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Contact info from full text
    email_match = _SECTION_PATTERNS["email"].search(text)
    if email_match:
        data["email"] = email_match.group(0)

    phone_match = _SECTION_PATTERNS["phone"].search(text)
    if phone_match:
        data["phone"] = phone_match.group(0).strip()

    linkedin_match = _SECTION_PATTERNS["linkedin"].search(text)
    if linkedin_match:
        data["linkedin"] = linkedin_match.group(0)

    github_match = _SECTION_PATTERNS["github"].search(text)
    if github_match:
        data["github"] = github_match.group(0)

    # Detect sections by scanning lines
    current_section = None
    section_content: dict = {}

    for i, line in enumerate(lines):
        matched_section = None
        for section_name in ("education", "experience", "skills", "projects", "summary", "certifications"):
            if _SECTION_PATTERNS[section_name].match(line):
                matched_section = section_name
                break

        if matched_section:
            current_section = matched_section
            section_content[current_section] = []
        elif current_section and line:
            section_content[current_section].append(line)

    # Convert lists to strings and add to data
    for section, content_lines in section_content.items():
        if content_lines:
            data[section] = " | ".join(content_lines[:8])  # cap at 8 lines per section

    # Try to guess name from first non-empty line if no email line precedes it
    if "name" not in data and lines:
        candidate = lines[0]
        if len(candidate.split()) <= 5 and not any(c in candidate for c in ["@", "http", "linkedin"]):
            data["name"] = candidate

    return data
