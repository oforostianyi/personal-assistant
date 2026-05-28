# Contributing to Personal Assistant

This is a 4-person, 4-day team sprint. Read this file once before opening
your first PR.

## Branches

- `main` is **protected** — direct push is forbidden. Land via PR only.
- Create feature branches off `main`:
  ```
  git checkout main
  git pull
  git checkout -b feature/<module>-<task>
  ```
  Examples: `feature/notes-tagger`, `feature/contacts-fields`,
  `feature/tags-search`, `feature/ui-tables`.

## Commits

Format: `feat(<module>): <short imperative summary>`

Examples:
- `feat(notes): add Note model and NotesBook`
- `feat(tags): collect tags from both books`
- `feat(ui): render Contacts and Notes as Rich tables`

Use `fix(...)`, `docs(...)`, `chore(...)` as appropriate. The `<module>`
slug matches your owner area (`core`, `contacts`, `notes`, `tags`, `ui`,
`docs`, `infra`).

## Pull Requests

1. Move your Trello card to **In Progress**.
2. Open the PR with **base = `main`**, **compare = your feature branch**.
3. Fill in the PR template (Summary / Changes / Test plan / Trello link).
4. Move the Trello card to **In Review**.
5. Wait for TL approval. SLA: ≤2 hours during working hours.
6. After approval: **Squash & merge** on GitHub. One PR ≡ one commit on
   `main` authored by you.
7. Move the Trello card to **Done**.

### What TL reviews

- Acceptance criteria from the Trello card are met.
- `python -m personal_assistant` still launches cleanly.
- Your handlers wear `@input_error`.
- Validators raise `ValueError(human-readable-message)` — do not return
  error strings from validators directly.
- Files live where the module brief says they live.

## Hard rules

- **`app.py` is TL-only.** Never edit it. Register your commands via
  `@command(...)` in your `handlers.py`. TL adds the import line during
  integration.
- **`core/*` is TL-only** after Stage-0.
- **No automated tests in scope.** Manual smoke checks only (run the app,
  exercise your new command, confirm output).
- **No new dependencies** without discussion in the team channel. Current:
  `rich`, `prompt_toolkit`, `rapidfuzz`.
- **Persistence files (`*.pkl`)** are gitignored. Never commit them.

## When you're blocked

Move the Trello card to **🐛 Blockers** and message the TL. Don't sit on
a problem — at 4 days, an hour lost matters.