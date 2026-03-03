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

## Deployment (public web app)

To make the service available publicly you need to host it on a machine or platform with Internet access and
run the FastAPI application there. The repository includes both a `Dockerfile` and
Firebase configuration so you can choose the workflow that fits you best.

### Firebase (hosting + backend)

If you already use Firebase, you can host the frontend on Firebase Hosting and deploy the
FastAPI backend to Cloud Run. The included `firebase.json` rewrites `/api/**` requests to a
Cloud Run service named `cobalt-core-backend` in `us-central1`.

1. Install the Firebase CLI and login:
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase init hosting
   # choose the existing project or create one, set "public" to "frontend" and agree to rewrites
   ```
2. Edit `.firebaserc` and `firebase.json` with your project ID and desired region/service name.
3. Deploy the backend via Cloud Run (example using gcloud):
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cobalt-core
   gcloud run deploy cobalt-core-backend \
     --image gcr.io/YOUR_PROJECT_ID/cobalt-core \
     --region us-central1 --platform managed --allow-unauthenticated \
     --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY,DATABASE_URL=$DATABASE_URL"
   ```
4. Deploy the frontend:
   ```bash
   firebase deploy --only hosting
   ```

On Firebase the API calls are proxied automatically, so the existing JavaScript (which
uses `API_BASE = ''`) works without change. You can also serve the frontend from GitHub
Pages or another host; just set `API_BASE` to the full URL of your backend.

### Container-based (recommended)

1. Build the included Docker image:
   ```bash
   docker build -t cobalt-core .
   ```
2. Push to your container registry (Docker Hub, GitHub Container Registry, etc.) or let your
   hosting service build from the repo directly.
3. Deploy the container on a service such as Render, Fly.io, Heroku (container stack), DigitalOcean App Platform,
   AWS ECS/Fargate, Google Cloud Run, etc.

Make sure you set the environment variables `OPENAI_API_KEY` (required) and optionally
`DATABASE_URL` (e.g. a PostgreSQL URI) in the platform's settings. The default command
runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`; you can override it with a
production-grade command like:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --workers 4
```

Once deployed, access the frontend by visiting the public URL provided by the host. All
frontend interactions (resume upload, interview, feedback) will then work exactly as they do
locally.

### Non-container deployment

If you prefer to deploy directly to a VM or bare-metal server, just install Python 3.13+ and
use the same steps as in **Installation** to set up a virtual environment and dependencies.
Run:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

or with Gunicorn for multiple workers. Configure your web server (Nginx, Caddy, etc.) to reverse-proxy
traffic to the application and to serve static files from the `frontend/` directory if desired.

A domain name and proper TLS certificate (Let's Encrypt) are recommended for production.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
