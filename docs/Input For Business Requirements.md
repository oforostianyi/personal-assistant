# Personal Assistant - Business Requirements Source Notes

## Purpose

This document records the source decisions used to keep the business, functional, architecture, and UI documents aligned with the current `main` branch.

## Reference Materials

| Source | What It Contributes |
| :---- | :---- |
| Current `main` branch | Integrated hierarchical/context-aware implementation |
| README.md | User behavior, launch commands, walkthrough, and seed checks |
| `personal_assistant/app.py` | Context dispatch, global navigation, entity-enter, auto-show |
| `personal_assistant/core/state.py` | Module/entity state and prompt rules |
| `personal_assistant/core/registry.py` | Context-aware command registration |
| `personal_assistant/seed.py` | Demo data loader for review |
| Launcher scripts | Easier local execution on macOS/Linux/Windows |

## Product Decisions

| Area | Decision |
| :---- | :---- |
| Product type | Offline Python terminal REPL for personal contacts, notes, tags, and birthdays |
| Navigation | Hierarchical/context-aware REPL: root -> module -> entity |
| Interface | Terminal prompts such as `>`, `contacts>`, and `contacts/Alice Johnson>` |
| Storage | Local pickle files under `~/.personal-assistant/` |
| Notes | Notes are opened by title in the UI and keep stable UUIDs internally |
| Demo support | `python -m personal_assistant.seed --force` creates 15 contacts and 15 notes |
| Launch support | `python -m personal_assistant`, `personal-assistance.sh`, `personal-assistance.bat` |
| AI / analytics | No AI integrations or analytics; fuzzy suggestions only |
| Deployment | Local machine, single user, no cloud services |

## Scope Summary

In scope:

- Context-aware root, module, and entity navigation.
- Contact create/view/edit/delete/search/sort/filter by tag and birthday lookup.
- Note create/view/edit/rename/delete/search/sort/filter/tag/link/unlink with multi-line body input.
- Tag list/search/sort/view/contacts/notes/rename/merge/delete across contacts and notes.
- Global search across contacts and notes.
- Tab completion, context help, fuzzy suggestions, Rich tables/cards, and friendly errors.
- Local persistence, demo seed loader, launcher scripts, and README walkthrough evidence.

Out of scope:

- Web, mobile, or desktop GUI.
- Multi-user accounts, authentication, permissions, or synchronization.
- SQL database, cloud storage, remote APIs, telemetry, or AI model integrations.
- Commercial monetization.

## Consistency Rules

| Topic | Required Value |
| :---- | :---- |
| Product interface | Offline terminal REPL |
| Navigation | Context-aware hierarchy with root/module/entity prompts |
| Storage | Local pickle files |
| Demo data | 15 contacts and 15 notes via seed loader |
| AI scope | No AI integrations; fuzzy suggestions only |
| GUI scope | No web/mobile/desktop GUI |
| Birthday format | `DD.MM.YYYY` |
| User model | Single local user |
