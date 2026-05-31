# Contacts Module

## Responsibility

The contacts module owns contact fields, records, the contacts book, contact commands, birthday lookup, and contact-side note links.

## Main Files

- `personal_assistant/contacts/fields.py` — `Name`, `Phone`, `Email`, `Address`, `Birthday`, `Tag`.
- `personal_assistant/contacts/record.py` — `Record` with phones, optional email/address/birthday, tags, linked note IDs, and timestamps.
- `personal_assistant/contacts/book.py` — `ContactsBook`, search/sort/filter helpers, birthday lookup, and note-link support.
- `personal_assistant/contacts/handlers.py` — context commands for contacts module and contact entity views.

## User Contexts

| Context | Prompt | Main Behavior |
|---|---|---|
| Contacts module | `contacts>` | `list`, `sort`, `find`, `filter tag`, `new`, `birthdays`, `search` |
| Contact entity | `contacts/NAME>` | `show`, `notes`, `edit`, field edits, tag edits, `delete` |

## Acceptance

- Contacts can be created, viewed, edited, deleted, searched, sorted, and filtered by tag.
- Phone, email, birthday, and tag validation return friendly errors.
- Birthday lookup supports `DD.MM.YYYY` birthdays and user-selected day ranges.
- Contact cards show linked notes where available.
- Changes persist after `exit` and relaunch.
