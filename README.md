# Cobalt Core: AI-Powered Interviewer

**Cobalt Core** is an intelligent mock interview platform designed to help engineers bridge the gap between their resume and the technical interview. Built with a focus on high-performance logic and minimalist design.

## Features

### 🎤 **Core Interview Modes**
- **Text Mode**: Type answers and receive AI feedback
- **Video Mode**: Record audio responses, transcribed & evaluated by AI

### 🧠 **AI-Powered Features**
- **Advanced Question Generation**: Context-aware questions based on resume, role, and conversation history
- **Real-time Feedback**: AI evaluates answers for:
  - Technical accuracy
  - Communication clarity
  - Strengths and improvement areas
  
### 📊 **Rich Feedback Analysis**
- **Vocabulary Diversity Score**: Measures word variety (0-100%)
- **Clarity Score**: Evaluates sentence structure and pacing
- **Filler Word Detection**: Identifies "um", "like", "you know", etc.
- **Repeated Word Analysis**: Highlights overused terms
- **Grammar Check**: Detects common mistakes
- **Hesitation Scoring**: Tracks speech hesitations

### 🎙️ **Voice Features**
- **Audio Transcription**: OpenAI Whisper for accurate speech-to-text
- **Text-to-Speech**: AI generates voice feedback (Google TTS)
- **Natural Conversation Flow**: AI responds with next question after each answer

### 💾 **Persistent Sessions**
- **Session Storage**: All interviews saved in database
- **Interview History**: View past sessions with Q&A records
- **Session Analytics**: Track score progression

### 📱 **User Interface**
- **Tabbed Interface**: Resume, Interview, Feedback, History sections
- **Real-time Feedback Display**: Instant scoring after each answer
- **Visual Analytics**: Score cards showing vocabulary and clarity metrics
- **Session Retrieval**: Browse and review past interviews


### Configuration

- Set `OPENAI_API_KEY` in your environment to enable real AI question generation, transcription, and analysis.
- Optionally specify `DATABASE_URL` (e.g. `sqlite:///cobalt.db` or a PostgreSQL URL) to persist interview sessions. Defaults to `sqlite:///cobalt.db`.

## Tech Stack
- **Backend:** Python (FastAPI)
- **AI Engine:** OpenAI (GPT-3.5, Whisper, TTS)
- **Database:** SQLAlchemy + SQLite/PostgreSQL
- **Environment:** Debian 13 (XFCE)
- **Frontend:** HTML5, Vanilla JavaScript
- **Audio Processing:** Google TTS (gTTS), OpenAI Whisper


## Installation
1. Clone the repo: `git clone https://github.com/YourUsername/ai-interviewer.git` or use the existing workspace.
2. Change to project directory and create a virtual environment:
   ```sh
   cd Cobalt-Core
   python3 -m venv venv && source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```
5. Start the development server. If `uvicorn` isn't in your PATH you can invoke it as a module without needing `sudo`:
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

## API Endpoints

### Core Endpoints
- `POST /upload_resume` – Parse resume (PDF/TXT/DOCX)
- `POST /start_interview` – Create new session, get first question
- `POST /submit_answer` – Submit text answer, get evaluation & next question
- `POST /video_audio` – Submit audio, transcribe, evaluate
- `POST /feedback` – Analyze transcript for vocabulary, grammar, filler words

### Advanced Features
- `POST /ai_voice_response` – Get AI-generated voice feedback (TTS)
- `GET /sessions` – List all past interview sessions
- `GET /sessions/{session_id}` – Retrieve specific session details
- `POST /end_session` – Finalize session and compute final score

## Environment Setup

1. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_key_here
   DATABASE_URL=sqlite:///cobalt.db
   ENVIRONMENT=development
   ```

2. Install dependencies as noted above.

3. Run the server and visit `http://localhost:8000` in your browser.


You can create simple HTTP requests to the endpoints defined in `app/main.py` (e.g. `/upload_resume`, `/start_interview`, `/feedback`).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
