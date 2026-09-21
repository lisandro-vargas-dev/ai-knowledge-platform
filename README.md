# AI Knowledge Platform

Minimal backend foundation for the AI Knowledge Platform (Milestone 1).

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

## Running Automated Tests

Run pytest from the `backend/` directory:

```powershell
cd C:\Projects\Antigravity\ai-knowledge-platform\backend
.\.venv\Scripts\python.exe -m pytest -q
```

## Starting the Server

Start the FastAPI application with Uvicorn bound locally to `127.0.0.1:8000`:

```powershell
cd C:\Projects\Antigravity\ai-knowledge-platform\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Verifying the Health Endpoint

With the server running, in a separate PowerShell session run:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health -Method Get
```

Expected output:

```json
{
  "status": "ok"
}
```

Or using `curl.exe`:

```powershell
curl.exe -s http://127.0.0.1:8000/health
```
