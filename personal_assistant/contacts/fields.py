"""Contact-specific fields.

Stage 1: Name, Phone, Birthday. Stage 3 adds Email, Address, and Tag:
a shared slug used by contacts and notes because tags are a cross-cutting
concept. Tag validation accepts Unicode letters, so non-Latin tags are valid
too.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from personal_assistant.core.fields import Field


class Name(Field):
    """Contact name field. Required."""

    value: str

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    """Phone number field.

    Always stored in canonical form: 10 digits without a prefix
    (`0631234567`). Input may contain any separators: spaces, parentheses,
    hyphens, plus signs, and the international `+380` / `380` prefix. This
    means `(063) 32-32-777`, `+380631234567`, `380 63 1234567`, and
    `0631234567` all normalize to the same value, so `remove`/`edit` work
    regardless of how the user entered the number the first time.
    """

    value: str

    @staticmethod
    def _normalize(raw: str) -> str:
        """Keep only digits; `380XXXXXXXXX` (12 digits) -> `0XXXXXXXXX`."""
        digits = re.sub(r"\D", "", raw or "")
        if len(digits) == 12 and digits.startswith("380"):
            digits = "0" + digits[3:]
        return digits

    def __init__(self, value: str) -> None:
        normalized = self._normalize(value)
        if len(normalized) != 10 or not normalized.isdigit():
            raise ValueError(
                f"Phone number '{value}' is invalid. "
                "Use 10 digits (e.g. 0631234567), with optional separators "
                "or +380/380 prefix."
            )
        super().__init__(normalized)


class Birthday(Field):
    """Birthday in DD.MM.YYYY format."""

    DATE_FORMAT = "%d.%m.%Y"
    value: date

    def __init__(self, value: str) -> None:
        try:
            parsed = datetime.strptime(value, self.DATE_FORMAT).date()
        except (TypeError, ValueError):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(parsed)

    def __str__(self) -> str:
        return self.value.strftime(self.DATE_FORMAT)


_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", re.UNICODE)


class Email(Field):
    """Email with simple regex validation."""

    value: str

    def __init__(self, value: str) -> None:
        v = (value or "").strip()
        if not _EMAIL_RE.match(v):
            raise ValueError(f"Email '{value}' is invalid.")
        super().__init__(v)


class Address(Field):
    """Address. At least 3 characters after trimming whitespace."""

    value: str

    def __init__(self, value: str) -> None:
        v = (value or "").strip()
        if len(v) < 3:
            raise ValueError("Address must be at least 3 characters.")
        super().__init__(v)


_TAG_RE = re.compile(r"^[\w-]+$", re.UNICODE)


class Tag(Field):
    """Tag as a slug (letters + digits + `_` + `-`).

    Unicode letters are also allowed (`\\w` in Python 3 includes Cyrillic by
    default). A leading `#` is stripped and the value is lowercased. This is
    the same type used by both contacts and notes, so the virtual `tags`
    module can aggregate from both sides without extra conversion.
    """

    value: str

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Tag must be a string.")
        v = value.strip().lstrip("#").strip().lower()
        if not v:
            raise ValueError("Tag cannot be empty.")
        if not _TAG_RE.match(v):
            raise ValueError(
                f"Tag '{value}' is invalid. Use letters, digits, '_' or '-' only."
            )
        super().__init__(v)
