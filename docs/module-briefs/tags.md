# Tags module — brief

**Owner:** Person 3.

Tags are a **virtual** module: no separate pickle file. Tags live as
strings on records (in `Record.tags`) and on notes (in `Note.tags`).
Aggregating, renaming, merging — all happen by walking both books.

## Files you create

- `personal_assistant/tags/aggregator.py` — `collect_tags(state)
  -> list[Tag]` where `Tag` is a small dataclass `{ name: str,
  contact_count: int, note_count: int }`. Walks `state.contacts.data`
  and `state.notes.data`, deduplicates, counts usages.
- `personal_assistant/tags/handlers.py` — commands listed below.

## Commands you register

| name | format | help |
|---|---|---|
| `list-tags` | | All tags + their usage counts (table). |
| `find-by-tag` | `<tag>` | Contacts AND notes that use this tag. |
| `sort-by-tag` | | List tags sorted by usage descending. |
| `rename-tag` | `<old> <new>` | Replace `old` with `new` everywhere. |
| `merge-tags` | `<tag1> <tag2>` | Replace `tag1` with `tag2` everywhere; delete `tag1`. |

## Dependencies you need

- `state.contacts`, `state.notes` (read both, mutate both for
  rename/merge).
- `core.registry.command`, `core.decorators.input_error`.
- `ui.tables.render_tags(tags)` — Person 4 builds (or you may render
  to plain text initially).

## Acceptance

- `list-tags` returns a table sorted alphabetically by tag name.
- `find-by-tag work` returns a combined view of all contacts and
  notes tagged `work`.
- `rename-tag work job` updates every record and note in both books.
  After this command, `find-by-tag work` returns nothing,
  `find-by-tag job` returns the same items as before the rename.
- `merge-tags personal private` after which `personal` is gone and
  `private` includes everything that was on either.
- Exit & relaunch — renames persisted (because they mutated the books).

## Notes & coordination

- Person 3 has the **smallest scope**. If you finish your tickets
  before D2 evening, ask the TL — you become the "floating helper"
  (fill gaps wherever needed).
- `Tag` field validation (lowercase, no spaces) is implemented in the
  Contacts module's `fields.py` — reuse, don't re-define.