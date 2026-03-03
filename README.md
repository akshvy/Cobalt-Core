# Cobalt Core: AI-Powered Interviewer

**Cobalt Core** is an intelligent mock interview platform designed to help engineers bridge the gap between their resume and the technical interview. Built with a focus on high-performance logic and minimalist design.

## Features
- **Resume Parsing:** Upload your PDF/Text resume for a tailored experience.
- **Dynamic Questioning:** AI generates technical and behavioral questions based on the Job Role.
- **Real-time Feedback:** Detailed analysis of your performance after each session.

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
