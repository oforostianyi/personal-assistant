# Personal Assistant

A console "Personal Assistant" — manages **contacts**, **notes**, and **tags**
through a single REPL. Built collaboratively as the final project of a Python
Programming course.

## Features (scope of this project)

- Contacts: add / edit / delete / find / list; phone / email / address /
  birthday / tags.
- Notes: add / edit / delete / find / list / link-to-contact (M:N).
- Tags: auto-extract from note text; find-by-tag; rename / merge tags
  across both books.
- Persistence: pickle files under `~/.personal-assistant/`.
- UX: Tab completion, format hints in the bottom toolbar, fuzzy
  "did you mean?" on typos.

**Out of scope:** hierarchical REPL navigation, database, automated tests,
CI, cloud sync, AI integrations.

## Install & run

```bash
pip install -r requirements.txt
python -m personal_assistant