# Personal Assistant

# Business Requirements

## Background

Personal Assistant is a console CLI application created as a final team project for a Python programming course. The original assignment requires a system for storing and interacting with contacts and notes, including validation, search, editing, deletion, and persistence across restarts. The current integrated product expands the scope with tags, note-contact links, contextual navigation, entity views, rich table rendering, fuzzy command suggestions, launcher scripts, and a demo seed loader.

## Business Problem or Opportunity

Users need one lightweight offline tool to manage personal contacts and notes from the command line. Without the product, contact data, birthdays, and notes can be scattered across unrelated files or tools. The opportunity is to provide a small but complete personal information assistant that also demonstrates course-level Python engineering skills.

## Business Objectives

- Deliver contact management with validated phone numbers, email, address, birthday, and tags.
- Deliver note management with text storage, search, edit, delete, tags, and links to contacts.
- Persist contacts and notes in the user's home directory.
- Provide a context-aware REPL with root, module, and entity prompts.
- Provide help, tab completion, fuzzy command suggestions, and readable Rich table/card output.
- Provide demo seed data and launcher scripts so review can start quickly.
- Produce final documentation and walkthrough evidence for course defense.

## Success Metrics

- The README manual walkthrough passes from a fresh clone after dependency installation.
- The original exercise checklist is covered: contacts, notes, validation, search, editing, deletion, birthdays, persistence, tags, and command suggestions.
- Data remains available after `exit` and relaunch.
- `python -m personal_assistant.seed --force` creates the expected 15 contacts and 15 notes for demo use.
- Launcher scripts start the application on supported platforms when dependencies are installed.
- README has no unresolved draft markers and matches the actual REPL behavior.

## Vision Statement

Personal Assistant is an offline console application that helps users manage contacts, notes, birthdays, and tags through a contextual Python REPL. It is designed to feel like a small terminal workspace: users enter `contacts`, `notes`, or `tags`, open entities by name/title/tag, work inside that context, and return with `..` or `/`.

## Business Risks

- **Documentation drift risk:** requirements, README, and code can diverge as the REPL behavior evolves.
- **Seed data risk:** the demo seed command overwrites local pickle files when run with `--force`.
- **Data compatibility risk:** stale pickle files may contain older structures.
- **Scope risk:** optional or stretch features can distract from core assignment requirements.
- **Demo risk:** manual walkthrough quality depends on seed data, terminal support, and installed dependencies.

Mitigations include aligning docs to the current `main`, warning users before demo seed overwrite, running syntax and seed sanity checks, and keeping web/cloud/AI features out of scope.

## Business Assumptions and Dependencies

Assumptions:

- The application targets local CLI use, not web or cloud deployment.
- Pickle persistence is acceptable for the project scope.
- Manual smoke tests are sufficient for the course requirements.
- Reviewers can run Python locally and use a terminal.

Dependencies:

- Python runtime and dependencies from `requirements.txt`: `rich`, `prompt_toolkit`, and `rapidfuzz`.
- Local filesystem access to `~/.personal-assistant/`.
- Launcher scripts: `personal-assistance.sh` and `personal-assistance.bat`.
- Demo seed loader for reproducible manual testing.

## Stakeholder Profiles

### End User

- **Category:** Primary user.
- **Benefits:** Stores contacts and notes, finds information quickly, receives birthday reminders and command suggestions.
- **Possible negative effects:** Must learn command syntax and use a terminal.
- **Constraints:** Needs local Python environment and filesystem access.

### Course Curator / Evaluator

- **Category:** Reviewer.
- **Benefits:** Can evaluate a complete team project against the assignment checklist.
- **Possible negative effects:** Incomplete integration or missing documentation makes review harder.
- **Constraints:** Needs a reproducible demo and clear README.

### Team Lead

- **Category:** Project integrator.
- **Benefits:** Maintains architecture consistency and validates final integration.
- **Possible negative effects:** Becomes a bottleneck if docs and code diverge.
- **Constraints:** Must preserve the context-aware navigation model in code and docs.

### Module Owners

- **Category:** Developers for Contacts, Notes, Tags, and UI.
- **Benefits:** Clear ownership and focused branches.
- **Possible negative effects:** Dependencies can block later cards.
- **Constraints:** Must follow module boundaries and avoid TL-only files.

## Solution Boundaries

### Functional boundaries

The solution includes these feature groups:

1. Contact management.
2. Birthday lookup.
3. Note management.
4. Note-contact linking.
5. Tag aggregation and tag operations.
6. Context-aware REPL command dispatch and navigation.
7. UI rendering, help, completion, and entity views.
8. Local persistence.
9. Demo seed data and easy run scripts.
10. Final documentation and walkthrough evidence.

### User interfaces boundaries

The only user interface is a console REPL. Users type commands at context prompts such as `>`, `contacts>`, `notes>`, `tags>`, and `contacts/Alice Johnson>`. Output is text, Rich tables, or Rich-style entity cards. There are no web, mobile, desktop GUI, or admin portals.

### Interfaces with external systems

The application does not integrate with external services. It uses:

- Local filesystem for pickle persistence.
- GitHub and Trello for project workflow and documentation references.
- Python packages listed in `requirements.txt`.

## Major Features

### F-01 Contact Management [MVP]

**Objective:** Store and maintain personal contacts.

Capabilities:

- Add contact with name and phone.
- View a contact card.
- Edit phone, email, address, birthday, and tags.
- Delete contact.
- Search contacts.
- Sort contacts.
- Filter contacts by tag.
- List contacts.
- Validate phone and email.

### F-02 Birthday Lookup [MVP]

**Objective:** Show upcoming birthdays within a user-defined number of days.

Capabilities:

- Calculate upcoming birthday dates.
- Adjust weekend congratulation dates where implemented.
- Render results in readable output.

### F-03 Note Management [MVP]

**Objective:** Store and manage text notes.

Capabilities:

- Create a note with a title and multi-line body.
- View a note card.
- Edit note body.
- Rename note title.
- Delete note.
- Search notes by title or body text.
- Sort and filter notes.
- List notes.
- Persist note UUIDs, titles, body text, timestamps, tags, and links across restarts.

### F-04 Note-Contact Linking

**Objective:** Maintain associations between notes and contacts.

Capabilities:

- Link a note to a contact.
- Unlink a note from a contact.
- Keep `Record.linked_note_ids` and `Note.linked_contact_names` synchronized.

### F-05 Tag Management [DIFFERENTIATOR]

**Objective:** Support tag-based organization across notes and contacts.

Capabilities:

- Extract hashtags from note text.
- Aggregate tags across both books.
- Find by tag.
- Sort by tag usage.
- View a tag entity.
- List contacts and notes for a tag.
- Rename, merge, and delete tags.

### F-06 Console UX [DIFFERENTIATOR]

**Objective:** Make the REPL easier to use.

Capabilities:

- Root/module/entity context prompts.
- Navigation with `contacts`, `notes`, `tags`, `..`, and `/`.
- Entity-enter by contact name, note title, or tag name.
- Contextual grouped help.
- Tab completion for commands and entities.
- Fuzzy command suggestion.
- Rich table and entity-card rendering.
- Parser support for quotes and whitespace edge cases.

### F-07 Persistence [MVP]

**Objective:** Preserve user data after application exit.

Capabilities:

- Save contacts to `~/.personal-assistant/contacts.pkl`.
- Save notes to `~/.personal-assistant/notes.pkl`.
- Reload saved data on next launch.

### F-08 Demo and Easy Run Support [MVP]

**Objective:** Make the project easy to review and demonstrate.

Capabilities:

- Run the app with `python -m personal_assistant`.
- Run platform launcher scripts where supported.
- Seed demo data with 15 contacts and 15 notes.
- Provide README verification commands and a manual walkthrough.

## Limitations and Exclusions

The product excludes:

- SQL database or cloud storage.
- Multi-user access control.
- Web or mobile UI.
- AI integrations.
- Automated test suite as a formal project deliverable.
- Synchronization across devices.

## Deployment Plan

Deployment is local and single-user:

1. Clone the GitHub repository.
2. Create and activate a Python virtual environment.
3. Install dependencies from `requirements.txt`.
4. Run `python -m personal_assistant`.
5. Optionally run `python -m personal_assistant.seed --force` to load demo data.
6. Use `help` inside the REPL.
7. Optionally start through `./personal-assistance.sh` or `personal-assistance.bat`.
6. Exit with `exit`; data is saved automatically.

No infrastructure changes, tenants, servers, or network services are required. Training consists of README instructions, command help, and the final smoke-test/demo script.
