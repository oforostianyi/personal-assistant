# Notes module — brief

**Owner:** Person 2.

## Files you create

- `personal_assistant/notes/note.py` — `Note(id: UUID, text: str,
  tags: list[str], linked_contact_names: list[str], created_at:
  datetime, updated_at: datetime)`. Methods: `add_tag`, `remove_tag`,
  `link_contact(name)`, `unlink_contact(name)`. `__str__` shows first
  60 chars + tags.
- `personal_assistant/notes/book.py` — `NotesBook(UserDict[UUID,
  Note])`. Methods: `add_note(text)` (returns the new Note), `delete`,
  `find_by_text(query)` (substring, case-insensitive), `find_by_tag`,
  `sort_by_tag`, `list_all`.
- `personal_assistant/notes/tagger.py` — `extract_tags(text: str,
  known_tags: set[str]) -> list[str]`. Two sources: explicit `#hashtag`
  in the text + words from the text that intersect `known_tags`.
  Filter a small stopword list (English + Ukrainian common words).
- `personal_assistant/notes/text_parser.py` — `extract_phones(text)`
  returns 10-digit sequences. `suggest_contacts(text, contacts_book)`
  returns `list[str]` of contact names fuzzily matched (rapidfuzz
  cutoff 80) to any capitalized token in the text.
- `personal_assistant/notes/handlers.py` — commands listed below.

## Commands you register

| name | format | help |
|---|---|---|
| `add-note` | `<text>` | Create a note; auto-extract tags + suggest contacts to link. |
| `edit-note` | `<id> <new text>` | Replace note text (re-runs tagger). |
| `delete-note` | `<id>` | Remove a note. |
| `find-note` | `<query>` | Substring search in note text. |
| `find-by-tag` | `<tag>` | All notes with this tag. |
| `list-notes` | | Table of all notes. |
| `link-note` | `<id> <contact_name>` | Link a note to a contact (M:N, both sides). |
| `unlink-note` | `<id> <contact_name>` | Reverse of link-note. |

## Dependencies you need

- `core.registry.command`, `core.decorators.input_error`,
  `core.fields.Field` — all in main.
- `state.contacts` — for `suggest_contacts` and `link-note`.
- `ui.tables.render_notes` — Person 4 builds.

## Acceptance

- `add-note "Meeting with John tomorrow #work, phone 0501234567"`
  returns: note id + extracted tags (`['work']`) + suggested links
  (`['John']` if John exists in contacts).
- `find-by-tag work` returns the same note.
- `link-note <uuid> John` — `John`'s `linked_note_ids` and the note's
  `linked_contact_names` both contain the link. Use the service in
  `contacts/book.py` — don't edit both sides yourself.
- Auto-tagger reinforces over time: adding a second note that mentions
  `work` tags it even without `#`, because `work` is now in
  `known_tags`.
- Exit & relaunch — notes persisted, UUIDs stable.

## Note IDs

Use `uuid.uuid4()` for new notes. The user never types a full UUID —
your handlers accept the first 8 hex chars as a prefix lookup. If
multiple notes match a prefix, return "Ambiguous: ... matches; type
more characters." If none match, raise `KeyError(prefix)` so
`@input_error` formats it.