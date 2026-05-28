"""Filesystem paths for app persistence.

All app data lives under `~/.personal-assistant/`. Distinct from any
older `addressbook.pkl` to avoid conflicts with previous coursework.
"""

from pathlib import Path

APP_DIR_NAME = ".personal-assistant"


def data_dir() -> Path:
    return Path.home() / APP_DIR_NAME


def ensure_data_dir() -> Path:
    p = data_dir()
    p.mkdir(parents=True, exist_ok=True)
    return p


def contacts_path() -> Path:
    return ensure_data_dir() / "contacts.pkl"


def notes_path() -> Path:
    return ensure_data_dir() / "notes.pkl"