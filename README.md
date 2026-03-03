# Cobalt Core: AI-Powered Interviewer

**Cobalt Core** is an intelligent mock interview platform designed to help engineers bridge the gap between their resume and the technical interview. Built with a focus on high-performance logic and minimalist design.

## Features
- **Resume Parsing:** Upload a PDF/TXT/DOCX resume and extract structured text.
- **Text-mode Interview:** type a role, get an AI‑generated question based on your resume, submit answers, receive simple scoring feedback.
- **Video-mode Interview:** record short audio clips via webcam/microphone; audio is sent to the server, transcribed by OpenAI Whisper, and evaluated.
- **Transcript Feedback:** paste any transcript to get repeated-word counts and basic grammar hints.
- **Frontend Web UI:** a single‑page HTML interface combining all functionality; persists interview history in JavaScript for context.
- **API Endpoints:** FastAPI backend with `/upload_resume`, `/start_interview`, `/submit_answer`, `/feedback`, and `/video_audio`.

## Tech Stack
- **Backend:** Python (FastAPI)
- **AI Engine:** Google Gemini AI
- **Environment:** Debian 13 (XFCE)
- **Database:** SQL (PostgreSQL/MySQL)

## Installation
1. Clone the repo: `git clone https://github.com/YourUsername/ai-interviewer.git` or use the existing workspace.
2. Change to project directory and create a virtual environment:
   ```sh
   python3 -m venv venv && source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the development server. If `uvicorn` isn't in your PATH you can invoke it as a module without needing `sudo`:
   ```sh
   python -m uvicorn app.main:app --reload
   ```
   It listens on `http://127.0.0.1:8000` by default; open that URL in your browser.

   > **Note:** you do **not** need root privileges to run the server. Avoid `sudo` unless you bind to a privileged port (<1024).

## Running Tests

You can run the simple unit tests using `pytest`:

```sh
pip install pytest
pytest
```

You can create simple HTTP requests to the endpoints defined in `app/main.py` (e.g. `/upload_resume`, `/start_interview`, `/feedback`).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
