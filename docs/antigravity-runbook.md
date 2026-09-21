# Antigravity Local M1 Runbook

This is an operational proposal for the user's existing Windows project. It does not replace `docs/project-spec.md`, authorize future phases, implement code, activate rules, or change settings automatically.

## Folder and surfaces

Expected repository: `C:\Projects\Antigravity\ai-knowledge-platform`.
Do not create a duplicate at `C:\Projects\ai-knowledge-platform` just because an older example used that path.

- Gemini web: advisory planning based on provided documents. In this workflow it has no direct access to the laptop.
- Antigravity desktop, Local mode: inspect the real repository, validate the plan, and later review changes.
- Antigravity CLI: implement and test the approved milestone in that same folder.
- Run only one modifying agent at a time. Do not assume automatic conversation/context synchronization. Use repository files for handoff.

## Suggested models (workflow choices, not benchmark claims)

- Gemini web: Pro, Standard thinking initially; Extended only for a genuinely difficult unresolved planning question and if available.
- Desktop local plan after the web discussion: Gemini 3.8 Flash, Medium. Do not repeat the entire architecture exercise.
- CLI implementation: Gemini 3.8 Flash, Medium.
- Independent review: Claude Sonnet 4.6 (Thinking).
- Escalation: Gemini 3.1 Pro High or Claude Opus 4.6 (Thinking) for one specific hard issue, not every task.

Use exact options available in the UI; do not invent a model slug or flag. `Verbosity: high` is a display setting, not the model's reasoning effort.

## Rules activation

1. Copy `.agents/rules/project-policy.md` to the repository root-relative location.
2. Select the correct project in the desktop app.
3. Open Customizations from the application menu or project settings, then the Rules tab.
4. Select the existing `project-policy` rule and choose Always on. If it does not appear, verify the folder and filename first. Create a workspace rule from the same content only if needed; avoid duplicate/global rules.
5. Preserve activation metadata written by the UI. Do not guess a frontmatter schema.
6. Open a fresh conversation / restart an idle CLI session to recheck loading.

The CLI `/settings` overlay is not this graphical Rules editor. The previous IDE-specific three-dot instructions are not the only entry point for the desktop app.

File existence is not proof of UI activation. Explicitly read the policy in the task prompts as a fallback. If rule-loading evidence is unavailable, report that uncertainty rather than claiming it is active.

## Settings to inspect in both surfaces

- Tool Permission / Terminal Command Auto Execution: request-review / Request Review.
- Non-Workspace Access: off; avoid granting broad outside-folder access.
- Use AI Credits: off in CLI; AI Credit Overages: Never in desktop.
- Enable Telemetry: off for this workflow; the latest supplied screenshot showed on. This does not make cloud inference offline or prevent all operational data processing.
- Sandbox Mode: the latest screenshot showed off. Enable the Windows preview if it is available and verify it with a harmless command through the permission flow. If it fails, report the exact error and do not auto-disable safeguards. Continuing without sandbox must be an explicit user decision with command-by-command review; never describe that fallback as isolated execution.
- Verbosity: high may stay on to inspect displayed actions. It is not reasoning effort.
- Agent Mode, if present: default, not accept-edits or unattended execution for this first trial.

No system administrator session, global permission changes, automatic remote publication, extra integrations, scheduled tasks, or parallel writers are required.

## Existing tools and local Python choice

The user reported CLI 1.2.7, Git 2.49.0.windows.1, and Python 3.11.9. Verify before use. These observations do not certify that every tool is up to date or secure.

Python 3.11 satisfies current published FastAPI requirements, but patch 3.11.9 has been superseded. Use it only for the controlled local M1 trial described here, with no sensitive data, uploads, public server, or paid API calls. Record a patched runtime update before deployment or handling untrusted documents. Do not silently install/update system tools.

Create `backend/.venv` only during approved implementation, using `py -3.11 -m venv .venv` from `backend/` if there is no existing environment. Invoke its Python directly, so activation-policy changes are unnecessary.

## Sequence

1. Confirm source documents and copy the setup payload without overwriting existing work blindly.
2. Activate the workspace rule and inspect permissions.
3. Use the Gemini web master prompt for advisory planning. Save only its English proposal at `docs/proposals/gemini-m1-plan.md` if used.
4. Desktop: inspect the real repository and prepare the local plan. No implementation or dependency installation.
5. User explicitly approves M1.
6. CLI: implement M1, test it, perform an actual HTTP smoke check, update progress, stop before commit.
7. Optional dedicated CLI verification: rerun existing tests and the HTTP check without source edits.
8. After the writer stops, use Sonnet for independent review. Source/config edits are not authorized by a review.
9. Approve only concrete fixes, reverify, and separately authorize a commit if desired.

## PowerShell versus CLI input

`PS C:\...>` is PowerShell: use `Set-Location`, `git`, `py`, and `agy` there.
Inside `agy`, use natural-language task prompts and slash commands such as `/settings`, `/model`, and `/usage`. Do not paste PowerShell setup commands into an agent prompt expecting the shell to execute them directly.

## CLI project association

Start from the verified repository with `agy --project="ai-knowledge-platform"` if that exact desktop project exists. CLI releases from 1.1.18 support project names. Verify the folder shown in the banner and the associated project. If it cannot find the project or the path differs, stop; inspect the actual project identifier/configuration rather than creating a duplicate. The ordinary `agy` launch can attach conversations to the default CLI project.

## M1 acceptance

- Actual tests executed and passed; show counts from output, not predictions.
- A separately started local server responds to GET /health with status 200 and JSON {"status":"ok"}.
- The interpreter and installation/test/run commands are recorded.
- Dependencies are reproducible under the selected approach.
- The README and saved reports are in English; conversational explanations are in Spanish.
- Changed and untracked files are reviewed.
- No provider SDK call, frontend, database, RAG, deployment, or automatic commit is introduced.

Use the README's actual commands once generated. Proposed structure-based examples are not evidence that the files already exist.

## Usage and costs

Take fresh `/usage` readings at task boundaries. Keep `docs/usage-log.md` based on observations. Family usage and quota reset windows can confound attribution. Do not promise a dollar amount from quota percentages.

M1 is designed to require no additional paid service and no application-provider API request; Antigravity still consumes included cloud-model quota. Your existing subscription or family arrangement is separate. AI credits off does not prevent a user-approved external script/API from charging another service, so this task explicitly forbids those calls.

M1 is not the complete AI MVP. M2 adds a separately configured provider API and M3 the React integration, under separate authorization and cost review.

## Official references checked for this guide

These references describe tools, not requirements that override the project specification. Interfaces may change; use actual local evidence.

- Rules across Antigravity surfaces: https://antigravity.google/docs/rules-workflows
- Settings: https://antigravity.google/docs/settings
- Windows agent permissions: https://antigravity.google/docs/agent-settings
- Terminal sandbox: https://antigravity.google/docs/sandbox?tab=cli
- Projects / CLI: https://antigravity.google/docs/projects?tab=cli
- CLI changelog (project-name flag support): https://www.antigravity.google/changelog
- Models: https://antigravity.google/docs/models
- Quotas: https://antigravity.google/docs/cli/commands/usage/
- Plans: https://antigravity.google/docs/plans
- Gemini uploads: https://support.google.com/gemini/answer/14903178?hl=en
- Gemini models and thinking levels: https://support.google.com/gemini/answer/16275805?hl=en
- Python 3.11.9 release status: https://www.python.org/downloads/release/python-3119/
- Python virtual environments: https://docs.python.org/3.11/library/venv.html
- FastAPI package metadata: https://pypi.org/project/fastapi/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
