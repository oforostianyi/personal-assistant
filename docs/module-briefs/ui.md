# UI module — brief

**Owner:** Person 4.

You own user-facing rendering and the help system. The completer and
fuzzy helpers are already in main (TL-owned, since they read the
registry directly).

## Files you create or extend

- `personal_assistant/ui/tables.py` (create) — `render_contacts(records,
  columns=None) -> str` and `render_notes(notes) -> str` and
  `render_tags(tags) -> str`. Build a `rich.Table` and return
  `Console(record=True).export_text()`. Handlers stay
  "return-a-string" — UI logic doesn't leak into them.
- `personal_assistant/ui/help.py` (create) — `render_help() -> str`
  walks `core.registry.primary_commands()` and returns a multi-line
  string grouped by module prefix (`add-contact`, `list-contacts`
  → "Contacts"; `add-note`, ... → "Notes"; etc.). Replace the
  built-in `help` handler in `app.py` once yours is ready — TL will
  do the swap during integration.
- `personal_assistant/ui/parser.py` (already exists, you may refine
  it — e.g. handle `--quoted-args` if the team needs them).

## Commands you register

- `help` — your version replaces the built-in. Register as
  `@command("help", aliases=("?",), help_="Show all commands.")`.
- (Stretch) one extra command of your choice — JSON export, alias
  `bd` for `birthdays`, etc. Coordinate with TL before adding.

## Dependencies you need

- `rich.Table`, `rich.Console` — already in `requirements.txt`.
- `core.registry.primary_commands()`.
- Models from contacts/notes/tags — but **only their fields**, never
  internal methods. (You render; you don't mutate.)

## Acceptance

- `list-contacts` displays a table with these columns: Name, Phones,
  Email, Birthday, Tags. Empty cells render as `—`.
- `list-notes` displays: ID (first 8 hex), Title/Preview (first 60
  chars), Tags, Linked, Created.
- `list-tags` displays: Tag, Contacts, Notes (counts).
- `help` shows all commands grouped by module, with format hints.
- A table over an empty list renders "No <items> yet." instead of an
  empty table border.

## Style

- Use `box.SIMPLE` or `box.ROUNDED` consistently.
- No colours that depend on terminal background (so demos look the
  same on light and dark).
- Truncate long fields with ellipsis (max 60 chars per cell).