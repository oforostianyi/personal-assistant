# Personal Assistant

Personal Assistant is a console application for managing contacts, notes, and
tags in one interactive REPL.

The app uses contextual navigation: from the root prompt you enter the
`contacts`, `notes`, or `tags` module, then work with lists or individual
entities inside that module.

## Features

- Contacts: create, view, edit, delete, search, sort, filter by tag, and show
  upcoming birthdays.
- Notes: create multi-line notes, view, edit, rename, delete, search, sort,
  filter, tag, and link notes to contacts.
- Tags: list usage statistics, search, rename, merge, and delete tags across
  both contacts and notes.
- Context-aware commands and prompts.
- Tab completion with `prompt_toolkit`.
- Context help through `help` or `?`.
- Fuzzy command suggestions for mistyped commands.
- Automatic data persistence between runs.
- Demo seed loader with 15 contacts and 15 notes for manual testing.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)

## Requirements

- Python 3.10 or newer.
- `pip` for dependency installation.
- Runtime dependencies from `requirements.txt`:
    - `rich`
    - `prompt_toolkit`
    - `rapidfuzz`

## Installation

1. Clone or unpack the project.

2. Go to the project root:

   ```bash
   cd personal-assistant
   ```

3. Create a virtual environment.

   Linux/macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Windows Command Prompt:

   ```bat
   py -3 -m venv .venv
   .venv\Scripts\activate.bat
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Running The App

The cross-platform entry point is:

```bash
python -m personal_assistant
```

The project also includes platform-specific launchers.

Linux/macOS:

```bash
./personal-assistance.sh
```

Windows:

```bat
personal-assistance.bat
```

The launcher scripts switch to the project root, prefer the local `.venv`
when it exists, check dependencies, clear the terminal, and start the app.

## Data Storage

Data is saved automatically when the app exits:

- contacts: `contacts.pkl`
- notes: `notes.pkl`

The files are stored in the user's home directory:

```text
~/.personal-assistant/
```

Typical locations:

- Linux: `/home/<user>/.personal-assistant/`
- macOS: `/Users/<user>/.personal-assistant/`
- Windows: `C:\Users\<user>\.personal-assistant\`

## Navigation Basics

After startup, the root prompt is shown:

```text
>
```

Global commands:

| Command             | Description                                     |
|---------------------|-------------------------------------------------|
| `help` or `?`       | Show commands available in the current context. |
| `contacts`          | Enter the contacts module.                      |
| `notes`             | Enter the notes module.                         |
| `tags`              | Enter the tags module.                          |
| `search <query>`    | Search both contacts and notes.                 |
| `birthdays [days]`  | Show upcoming birthdays.                        |
| `..`                | Move one level up.                              |
| `/`                 | Return to the root context.                     |
| `exit`, `quit`, `q` | Exit and save data.                             |

Inside a module, typing an entity name directly opens that entity when it
exists. For example, typing `Alice Johnson` at `contacts>` opens that contact.
If no entity matches, the app can offer to create a new contact or note.

## Contacts

Enter the contacts module:

```text
> contacts
contacts>
```

Commands at `contacts>`:

| Command                      | Description                                    |
|------------------------------|------------------------------------------------|
| `list`                       | List all contacts.                             |
| `sort <field> [asc or desc]` | Set the sort key for `list`.                   |
| `find <query>`               | Search by name, phone, email, address, or tag. |
| `filter tag <tag>`           | List contacts with the given tag.              |
| `new <name>`                 | Create a contact and enter it.                 |
| `birthdays [days]`           | Show upcoming birthdays.                       |
| `search <query>`             | Search both contacts and notes.                |

Contact sort fields:

```text
name, birthday, tags_count, created
```

Example:

```text
contacts> new John Smith
contacts/John Smith> edit phone add 0631234567
contacts/John Smith> edit email john@example.com
contacts/John Smith> edit birthday 12.05.1990
contacts/John Smith> edit tags add friends
contacts/John Smith> show
contacts/John Smith> ..
contacts> list
```

Commands inside one contact:

| Command                       | Description                            |
|-------------------------------|----------------------------------------|
| `show`                        | Show the contact card.                 |
| `notes`                       | List notes linked to this contact.     |
| `edit`                        | Open the interactive edit menu.        |
| `edit name <value>`           | Rename the contact.                    |
| `edit phone add <number>`     | Add a phone number.                    |
| `edit phone edit <old> <new>` | Replace a phone number.                |
| `edit phone remove <number>`  | Remove a phone number.                 |
| `edit email <value>`          | Set email.                             |
| `edit address <value>`        | Set address.                           |
| `edit birthday <DD.MM.YYYY>`  | Set birthday.                          |
| `edit tags add <tag>`         | Add a tag.                             |
| `edit tags remove <tag>`      | Remove a tag.                          |
| `delete`                      | Delete the contact after confirmation. |

## Notes

Enter the notes module:

```text
> notes
notes>
```

Commands at `notes>`:

| Command                      | Description                     |
|------------------------------|---------------------------------|
| `list`                       | List all notes.                 |
| `sort <field> [asc or desc]` | Set the sort key for `list`.    |
| `find <query>`               | Search by title or body text.   |
| `filter tag <tag>`           | List notes with the given tag.  |
| `filter contact <name>`      | List notes linked to a contact. |
| `new [title]`                | Create a note.                  |
| `search <query>`             | Search both contacts and notes. |

Note sort fields:

```text
title, created, updated, tag, contact
```

Example:

```text
notes> new Meeting notes
Text (blank line to finish, Ctrl+C to cancel):
> Discuss project timeline with John Smith.
> #work #meeting
>

notes/Meeting notes> link John Smith
notes/Meeting notes> tag planning
notes/Meeting notes> show
```

Commands inside one note:

| Command              | Description                                |
|----------------------|--------------------------------------------|
| `show`               | Show the note.                             |
| `edit`               | Edit the note body in a multi-line editor. |
| `rename <new title>` | Rename the note.                           |
| `tag <tag>`          | Add a tag.                                 |
| `untag <tag>`        | Remove a tag.                              |
| `link <contact>`     | Link the note to a contact.                |
| `unlink <contact>`   | Remove a contact link.                     |
| `delete`             | Delete the note after confirmation.        |

## Tags

Enter the tags module:

```text
> tags
tags>
```

Commands at `tags>`:

| Command                      | Description                      |
|------------------------------|----------------------------------|
| `list`                       | List all tags with usage counts. |
| `sort <field> [asc or desc]` | Set the sort key for `list`.     |
| `find <query>`               | Search tag names by substring.   |

Tag sort fields:

```text
name, usage, contacts, notes
```

Commands inside one tag:

| Command         | Description                        |
|-----------------|------------------------------------|
| `show`          | Show tag usage counts.             |
| `contacts`      | List contacts with this tag.       |
| `notes`         | List notes with this tag.          |
| `rename <new>`  | Rename the tag everywhere.         |
| `merge <other>` | Merge this tag into another tag.   |
| `delete`        | Remove this tag from all entities. |

Example:

```text
tags> list
tags> work
tags/work> contacts
tags/work> notes
tags/work> rename job
```

## Search And Completion

- Press `Tab` to complete commands or entity names in the current context.
- When a command is mistyped, the app suggests the closest command name.
- `search <query>` searches contacts and notes at the same time.

## Scope

In scope:

- Local single-user contact, note, birthday, tag, and link management.
- Context-aware terminal navigation with root, module, and entity prompts.
- Local pickle persistence under `~/.personal-assistant/`.
- Demo seed data for review and manual testing.
- Terminal help, completion, fuzzy suggestions, tables, and entity cards.

Out of scope:

- Web, mobile, or desktop GUI.
- Multi-user accounts, authentication, permissions, or synchronization.
- SQL database, cloud storage, remote APIs, telemetry, or AI model integrations.
- Commercial monetization.

## Demo Data

The project includes a demo data loader:

```bash
python -m personal_assistant.seed --force
```

It writes 15 contacts and 15 notes with shared tags, cross-links, and several
birthdays inside the next 7 and 30 days.

Important: this command overwrites the current `contacts.pkl` and `notes.pkl`
files in `~/.personal-assistant/`. Run it only when replacing the current local
data is acceptable.

Expected output:

```text
Seeded 15 contacts and 15 notes (21 contact↔note links).
Launch with:  python -m personal_assistant
```

## Review Evidence

Smoke verification was run on 2026-05-31 using an isolated temporary home
directory so local user data was not modified.

Passed checks:

- `python -m compileall -q personal_assistant`
- `python -m personal_assistant.seed --force`
- seed sanity check: 15 contacts, 15 notes, 2 Alice-linked notes, and
  `Project kickoff` tags `['project', 'work']`
- manual REPL walkthrough for root help, contacts, notes, tags, global search,
  birthdays, and exit persistence
- POSIX launcher check with `TERM=xterm ./personal-assistance.sh`

Note: `personal-assistance.sh` expects a terminal-like environment. In a
non-interactive pipe without `TERM`, the `clear` command may fail before the app
starts.

## Testing

There is no automated test suite in this project. Verification is done through
syntax checks, a seed-data sanity check, and a manual end-to-end walkthrough.

### Syntax Check

Run:

```bash
python -m compileall personal_assistant
```

Expected result: all modules compile without errors.

### Seed-Data Sanity Check

Load the demo database:

```bash
python -m personal_assistant.seed --force
```

Then verify saved object counts and links:

```bash
python -c "
from personal_assistant.core.storage import PickleStorage
from personal_assistant.core.paths import contacts_path, notes_path
from personal_assistant.contacts.book import ContactsBook
from personal_assistant.notes.book import NotesBook
s = PickleStorage()
c = s.load(contacts_path(), ContactsBook)
n = s.load(notes_path(), NotesBook)
print('contacts:', len(c.data), 'notes:', len(n.data))
alice = c.find('Alice Johnson')
print('Alice linked notes:', len(alice.linked_note_ids))
print('tags on a note:', [t.value for t in n.find_by_title('Project kickoff').tags])
"
```

Expected output:

```text
contacts: 15 notes: 15
Alice linked notes: 2
tags on a note: ['project', 'work']
```

### Manual Test Walkthrough

Before the walkthrough, run:

```bash
python -m personal_assistant.seed --force
python -m personal_assistant
```

Use the following commands in the REPL.

#### A. Navigation And Help

1. `help` should show the root context and list `contacts`, `notes`, `tags`,
   `birthdays`, `search`, and global commands.
2. `contacts` should switch to `contacts>`.
3. `..` should return to `>`.
4. `notes` should switch to `notes>`.
5. `/` should return to `>` from any context.

#### B. Contacts

1. `contacts`, then `list` should show a 15-row contacts table.
2. `sort birthday asc`, then `list` should show contacts with birthdays first.
3. `find Alice` should show Alice Johnson.
4. `filter tag vip` should show Alice Johnson and Diana Prince.
5. `Alice Johnson` should enter `contacts/Alice Johnson>` and auto-show the
   contact card.
6. `notes` inside that contact should show the linked Alice notes.

Contact editing checks:

```text
edit
6
a
priority
0
edit phone add 0991112233
show
..
new Test User
delete
y
```

Expected results: the `priority` tag is added, the extra phone appears in the
contact card, and `Test User` is deleted after confirmation.

#### C. Notes

1. `/`, then `notes`, then `list` should show 15 notes.
2. `sort tag asc`, then `list` should place tagless notes last.
3. `filter tag work` should show work-related notes.
4. `filter contact Ivan Petrov` should show notes linked to Ivan.
5. `Project kickoff` should enter the note and show its body, tags, and linked
   contacts.
6. `rename Project kickoff 2025` should rename the note and update the prompt.

Automatic tag and contact suggestion check:

```text
..
new Call Alice
Sync with Alice on 0631000001 about #planning and work

link Alice Johnson
show
edit
```

Expected after creating the note:

```text
Created note 'Call Alice'.
Auto tags: planning, work
Suggested contacts: Alice Johnson
Tip: from inside this note, use 'link <name>'.
```

Expected behavior:

- `planning` is added from the `#planning` hashtag.
- `work` is suggested because it already exists as a tag.
- `Alice Johnson` is suggested from the phone number and name match.
- `link Alice Johnson` makes the relationship visible in `show`.
- Adding `#finance` during `edit` adds the `finance` tag without removing
  existing tags.

#### D. Tags

1. `/`, then `tags`, then `list` should show all tags with contact/note counts.
2. `sort usage desc`, then `list` should show the most-used tags first.
3. `find dev` should show matching tags.
4. `dev` should enter `tags/dev>` and show counts.
5. `contacts` should list contacts tagged `dev`.
6. `notes` should list notes tagged `dev`.
7. `rename engineering` should rename the tag everywhere.
8. Enter `vip`, run `merge premium`, confirm with `y`, and verify `premium`
   replaces `vip` in the tag list.
9. Enter any tag, run `delete`, confirm with `y`, and verify the tag is removed
   from all entities.

#### E. Global Search, Birthdays, And Persistence

1. `/`, then `search Alice` should show Alice in contacts and Alice-related
   notes.
2. `birthdays` should show birthdays in the next 7 days.
3. `birthdays 30` should include contacts with birthdays in the next 30 days.
4. `exit` should print `Good bye!`.
5. Restart with `python -m personal_assistant`; previous edits should still be
   present, proving persistence works.

## Code Comments And Documentation

The codebase includes module-level docstrings for core modules and short
docstrings for important functions, classes, and command handlers. Comments are
kept where they explain behavior that is not obvious from the code itself, such
as:

- context-aware command registration;
- atomic pickle-file persistence;
- phone-number normalization;
- interactive edit flows;
- search, tag, and contact-note linking behavior.

Obsolete comments about old implementation stages, internal tickets, temporary
workarounds, and module ownership notes have been removed.

## Credits And Project History

Personal Assistant was implemented as a Python team project using feature
branches and GitHub pull requests. The final integrated `main` branch contains
the contextual REPL implementation, demo seed loader, launcher scripts, and
documentation updates.

Primary contribution areas:

- Core application, context registry, state, storage, and integration.
- Contacts domain: validation, records, book operations, birthdays, and contact
  commands.
- Notes domain: titled notes, multi-line body editing, tag extraction, contact
  suggestions, and note-contact links.
- Tags domain: virtual tag aggregation, tag entity views, rename, merge, and
  delete.
- UI: context help, completion, fuzzy suggestions, Rich tables/cards, and parser
  behavior.
- Documentation: requirements, architecture, smoke evidence, and README.

## Project Structure

```text
personal_assistant/
  app.py              # REPL loop and dispatcher
  seed.py             # demo-data loader
  core/               # state, registry, storage, paths, decorators
  contacts/           # contact fields, records, book, commands
  notes/              # note model, book, text parser, commands
  tags/               # tag aggregation and commands
  ui/                 # parser, completer, help, rich-based renderers
requirements.txt
personal-assistance.sh
personal-assistance.bat
```
