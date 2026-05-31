# Notes Module

## Responsibility

The notes module owns titled notes, multi-line note body editing, tag extraction, phone/name parsing, contact suggestions, and note-contact links.

## Main Files

- `personal_assistant/notes/note.py` — `Note` with UUID, title, text, tags, linked contact names, created/updated timestamps.
- `personal_assistant/notes/book.py` — `NotesBook` keyed by normalized title.
- `personal_assistant/notes/tagger.py` — hashtag and known-tag extraction.
- `personal_assistant/notes/text_parser.py` — phone extraction and contact suggestion helpers.
- `personal_assistant/notes/handlers.py` — context commands for notes module and note entity views.

## User Contexts

| Context | Prompt | Main Behavior |
|---|---|---|
| Notes module | `notes>` | `list`, `sort`, `find`, `filter tag`, `filter contact`, `new`, `search` |
| Note entity | `notes/TITLE>` | `show`, `edit`, `rename`, `tag`, `untag`, `link`, `unlink`, `delete` |

## Acceptance

- Notes can be created with a title and multi-line body.
- Note titles are unique case-insensitively.
- Notes keep stable UUIDs internally for links and persistence.
- Hashtags and known tags are applied to note text.
- Contact suggestions appear when note text references known contacts or phone numbers.
- Linked contacts are synchronized with contact-side linked note IDs.
- Notes can be searched, sorted, filtered, renamed, edited, deleted, and persisted.
