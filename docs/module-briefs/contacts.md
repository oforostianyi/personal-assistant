# Contacts module — brief

**Owner:** TL (Team Lead, also doing core + integration).

## Files you create

- `personal_assistant/contacts/fields.py` — `Name`, `Phone`, `Email`,
  `Address`, `Birthday`, `Tag`. Each subclasses `core.fields.Field` and
  validates in `__init__`, raising `ValueError("human message")` on bad
  input. Phone: 10 digits. Email: a single `@`, a dot in the domain.
  Birthday: `DD.MM.YYYY`, not in the future. Tag: lowercase slug.
- `personal_assistant/contacts/record.py` — `Record(name, phones, email,
  address, birthday, tags, linked_note_ids)`. Methods: `add_phone`,
  `edit_phone`, `remove_phone`, `add_email/edit_email`,
  `add_tag/remove_tag`, `link_note_id`, `unlink_note_id`. `__str__` for
  a one-line summary.
- `personal_assistant/contacts/book.py` — `ContactsBook(UserDict[str,
  Record])`. Methods: `add_record`, `find`, `delete`, `search(query,
  fields=(...))`, `upcoming_birthdays(days)`. Plus the M:N service
  `link_note(record, note)` (mutates both sides).
- `personal_assistant/contacts/handlers.py` — commands listed below,
  each decorated `@input_error` and `@command(...)`.

## Commands you register

| name | format | help |
|---|---|---|
| `add-contact` | `<name> <phone>` | Add a new contact with one phone. |
| `edit-contact` | `<name> <field> <value>` | Edit a single field. |
| `delete-contact` | `<name>` | Remove a contact. |
| `find-contact` | `<query>` | Substring search across all fields. |
| `list-contacts` | | Show all contacts as a Rich table (via `ui.tables`). |
| `birthdays` | `<days>` | Upcoming birthdays in the next N days. |

## Dependencies you need

- `core.fields.Field` (already in main).
- `core.registry.command` (already in main).
- `core.decorators.input_error` (already in main).
- `ui.tables.render_contacts(records, columns=None)` — Person 4 builds
  this. Until it lands, render with a simple text fallback.

## Acceptance

- All 6 commands work in `python -m personal_assistant`.
- `add-contact John 0501234567` → success message. Second add of same
  name → updates existing record (one record per name).
- `edit-contact John email john@example.com` → validation error if
  the email is malformed (catch via `@input_error`).
- `birthdays 30` → table of upcoming birthdays in the next 30 days,
  sorted by date (week-day display optional).
- `delete-contact John` → confirmation, second `list-contacts` doesn't
  show John.
- Exit & relaunch → all data still present.