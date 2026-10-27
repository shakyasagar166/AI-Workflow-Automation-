# AI Workflow Automation System — Setup Guide

Follow this guide to get the AI Workflow Automation System running locally or via Docker containers.

---

## Prerequisites
- **Python**: 3.10+ (Tested on Python 3.11, 3.12, 3.13)
- **Node.js**: 18+ and npm
- **Docker & Docker Compose** (Optional, for containerized deployment)

---

## 1. Quickstart with Docker Compose

To launch backend, worker, and frontend simultaneously:

```bash
cd infrastructure
docker-compose up --build
```

- **Frontend UI**: http://localhost:5173
- **FastAPI Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 2. Local Development Setup

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in `backend/` or copy from `.env.example`:
   ```bash
   cp ../.env.example .env
   ```

5. **Start the FastAPI backend server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Run tests**:
   ```bash
   python -m pytest app/tests -v
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node packages**:
   ```bash
   npm install
   ```

3. **Start Vite development server**:
   ```bash
   npm run dev
   ```

4. Open `http://localhost:5173` in your browser.

---

## 3. Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./workflow_automation.db` |
| `DEFAULT_API_KEY` | Admin API key | `ai-wf-key-default-admin-2026` |
| `MOCK_LLM_MODE` | Use built-in autonomous LLM simulation | `true` |
| `GEMINI_API_KEY` | Google Gemini API Key | `""` |
| `OPENAI_API_KEY` | OpenAI API Key | `""` |
| `DEFAULT_LLM_PROVIDER` | `gemini` or `openai` | `gemini` |
| `SMTP_HOST` | Outbound SMTP host | `smtp.example.com` |
| `SMTP_PORT` | Outbound SMTP port | `587` |
| `MAX_CONCURRENT_STEPS` | Concurrent steps in DAG executor | `5` |
