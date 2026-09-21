# M1 — Minimal FastAPI Backend

Status: proposed; awaiting inspection and user approval.

Source of truth: `docs/project-spec.md`, especially its Milestone 1 scope. This task does not authorize implementation merely by being present.

## Goal

Create the smallest reproducible backend foundation. This is an engineering milestone, not the complete AI MVP or a document-grounded RAG product.

## Before editing

Confirm the current directory, project name, Git root/status, existing files, Python version, Git version, and existing dependency strategy. Preserve unrelated changes. Do not assume an empty repository or missing implementation.

## Scope

- A small Python/FastAPI application under `backend/`, adapting to an existing layout if necessary.
- A local virtual environment and reproducible dependency configuration.
- `GET /health` with HTTP 200 and exactly `{"status":"ok"}`.
- A response schema when useful and minimal actual configuration.
- At least one test asserting both HTTP status and JSON body.
- An English README with exact Windows PowerShell commands.
- `.gitignore` that excludes virtual environments, generated caches, real `.env` files, and secrets while allowing `.env.example` when used.
- No invented framework layers or unused configuration variables.

## Explicitly out of scope

Frontend, provider API calls, authentication, workspaces as a product feature, document upload, ingestion, embeddings, RAG, PostgreSQL, Redis, Docker, deployment, remote publication, and automatic commits.

## Acceptance evidence

- Actual test command, exit result, and observed pass/fail summary.
- Actual server startup and a local HTTP request to `/health`, separate from TestClient testing.
- Exact environment and reproduction commands.
- Final file tree, diff, and inspection of new untracked files.
- Explicit list of unverified items and remaining issues.

Bind the server to `127.0.0.1`. Track only the server process started for the check and shut it down after verification. Do not stop unrelated Python processes or services.

## Handoff

During an authorized implementation, update `docs/progress.md` in English with the evidence and next step, and explain the result in Spanish. Do not infer quota or dollar cost from tokens, runtime, or intuition. Record those only from available observations.

Approval must be an explicit user instruction. Marking a checkbox or changing this status yourself is not approval.


## Operational proposal for this Windows test

The following are setup choices for this experiment, not additional product requirements:

- The user currently has Python 3.11.9. Check `py -3.11 -V` locally before use. Python 3.11 is compatible with the published FastAPI requirements, but the 3.11.9 patch is old. This is a local, non-sensitive smoke test; track upgrading to a currently patched Python installation before deployment or processing untrusted documents. A virtual environment does not patch the interpreter.
- Do not install or upgrade Python, Git, Antigravity, or machine-wide tools automatically. A missing or incompatible prerequisite is a blocker to report.
- When no environment exists, prefer `backend/.venv` using the installed Python 3.11 interpreter. If a usable environment or dependency strategy exists, inspect it and preserve it; do not create a conflicting second setup.
- Propose dependency versions compatible with the interpreter and verify them using primary package metadata. Do not guess exact latest versions. Record the actually resolved versions and reproducible installation instructions.
- Use `venv` and its Python/pip directly rather than adding a global package manager just for this milestone.
- The proposed import path is `app.main:app`, with commands run from `backend/`. Adapt only if existing code requires it and update the README accordingly.
- Proposed local checks after implementation: `.\.venv\Scripts\python.exe -m pytest -q` and `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- A port conflict does not authorize terminating another process. Use another local port and report it, or stop with the conflict.
- Public package downloads needed for the authorized implementation are allowed only through the normal tool review flow. Do not change sandbox or network settings to bypass a failed permission request.
- Keep one writing agent active at a time. A review/test-only request does not authorize feature changes.
- The task file must not be marked implemented or passed merely because these instructions exist.
