# Project Policy

## Language

- Respond to the user in Spanish by default, in both the desktop app and the CLI, even when the task instructions are written in English. Use another conversational language only when the user explicitly requests it.
- Keep all project-authored persistent technical material in English: specifications, rules, skills, workflow instructions, implementation plans, task files, walkthroughs, README files, architecture notes, test reports, code comments, docstrings, identifiers, test names, and proposed commit messages.
- A Spanish request or explanation does not authorize translating repository files into Spanish. Translate a particular artifact only when explicitly requested.
- Keep commands, file paths, API names, identifiers, error messages, and quoted terminal output verbatim. Explain their meaning in Spanish without altering the evidence.
- Preserve the original language of uploaded documents, quoted source material, and language-specific test data. Do not translate product content merely to satisfy the technical-documentation policy.
- Do not change application menus, operating-system locale, shell locale, or the product's UI-language requirements to implement this policy.

## Project context

- Read `docs/project-spec.md` before implementing or reviewing a milestone. Treat it as the product specification, not proof of implementation.
- Inspect the actual repository, current working directory, and Git status. Do not claim to have read files or run checks that were unavailable.
- Use only relevant project material. Do not introduce personal profiles, career plans, learning curricula, or unrelated product documents.
- Work on the milestone authorized in the current request. Installing these rules is not authorization to build the application.
- Do not advance to another milestone automatically. Distinguish planned, implemented, verified, and still-unverified work.

## Implementation requests

- Inspect the existing state, present a short plan, then implement the explicitly requested scope. Do not repeatedly ask for approval for routine choices within that scope.
- Keep the design small and maintainable. Add dependencies, abstractions, and infrastructure only when needed by the current milestone.
- Use the local project environment and existing dependency-management approach. Preserve unrelated changes.
- Add or update relevant tests, execute the available checks, and report their real results. During implementation, fix failures caused by your changes without expanding the feature scope.
- Keep saved technical plans, documentation, and reports in English; summarize the result for the user in Spanish.
- Show the changed files, including untracked files, and important diffs. Stop before committing, pushing, or advancing milestones unless explicitly authorized.

## Verification and review requests

- A request for project status or review is read-only by default. Inspect the code and available evidence; do not implement fixes or start new features.
- A request to run tests authorizes the existing relevant local test commands, not package installation, source edits, dependency changes, paid API requests, or deployment. Stop and report missing prerequisites.
- Normal local test-generated artifacts such as caches are acceptable during a test run; do not treat them as permission to modify source or configuration.
- Report executed commands, pass/fail results, skipped checks, blockers, and the next smallest step. Separate execution evidence from static inspection and inference.
- Do not claim all tests passed when checks were skipped or could not run. Do not invent test counts, coverage, latency, costs, or quotas.
- Present findings in Spanish. Keep any explicitly requested saved technical report in English.

## Safety and permissions

- Keep work scoped to the selected repository and the authorized task. Do not delete or overwrite unrelated work.
- Do not use administrator privileges or change global system configuration, PowerShell execution policies, or global package installations.
- Do not print, commit, or upload secrets. Use placeholders in example configuration and avoid inspecting unrelated personal files.
- Obtain explicit approval before paid API calls, purchases, deployment, remote repository publication, or destructive operations.
- Respect tool permission prompts. These Markdown instructions are behavioral guidance, not a filesystem sandbox or permission grant.
- If a tool, file, or check is unavailable, explain the limitation rather than claiming completion.
