# AI Knowledge Platform

AI-powered knowledge platform backend built with FastAPI, Pydantic, and OpenAI.

## Prerequisites

- Windows 11 (or 10) 64-bit
- Python 3.11+ (verified with Python 3.11.9 via `py -3.11`)
- Git

## Setup and Installation (Windows PowerShell)

Open PowerShell and navigate to the repository directory:

```powershell
cd C:\Projects\Antigravity\ai-knowledge-platform\backend
```

Create a local virtual environment:

```powershell
py -3.11 -m venv .venv
```

Upgrade `pip` and install dependencies directly using the virtual environment's Python binary (no execution policy changes required):

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment Configuration

Copy the example environment file to `.env`:

```powershell
Copy-Item .env.example .env
```

Configurable variables in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key (required only for real provider calls).
- `OPENAI_MODEL`: Model identifier (default: `gpt-4o-mini`).
- `OPENAI_BASE_URL`: Base URL for OpenAI-compatible endpoint (default: `https://api.openai.com/v1`).
- `OPENAI_TIMEOUT_SECONDS`: Request timeout in seconds (default: `30.0`).
- `OPENAI_MAX_RETRIES`: Automatic retry attempts on transient errors (default: `2`).
- `OPENAI_MAX_TOKENS`: Maximum output tokens (default: `1024`).
- `OPENAI_TEMPERATURE`: Sampling temperature (default: `0.7`).
- `DEBUG`: Enable debug-level logging (default: `false`).

## Running Automated Tests

Run the full pytest suite (44 tests with mocks, zero external network calls):

```powershell
cd C:\Projects\Antigravity\ai-knowledge-platform\backend
.\.venv\Scripts\python.exe -m pytest -v
```

## Starting the Server

Start the FastAPI application with Uvicorn bound locally to `127.0.0.1:8000`:

```powershell
cd C:\Projects\Antigravity\ai-knowledge-platform\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Verifying Endpoints

### 1. Health Endpoint (`GET /health`)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health -Method Get
```

Expected output:

```json
{
  "status": "ok"
}
```

### 2. Chat Completions Endpoint (`POST /chat/completions`)

```powershell
$body = @{
    messages = @(
        @{ role = "user"; content = "Hello! What is this platform?" }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/chat/completions -Method Post -Body $body -ContentType "application/json"
```

*Note: Requires a valid `OPENAI_API_KEY` configured in `.env` for live calls; returns HTTP 401 when unauthenticated.*
