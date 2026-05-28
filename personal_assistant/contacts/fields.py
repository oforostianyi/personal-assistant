"""Поля, специфічні для контактів.

Stage 1: Name, Phone, Birthday. Stage 3 додає Email, Address і Tag —
загальний slug, спільний для контактів і нотаток (бо теги — поняття
наскрізне). Tag валідація приймає юнікодні літери, тож українські
теги (наприклад, `робота`) теж пройдуть.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from personal_assistant.core.fields import Field


class Name(Field):
    """Поле імені контакту. Обов'язкове."""

    value: str

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    """Поле номера телефону.

    Зберігається завжди у канонічній формі: 10 цифр без префіксу
    (`0631234567`). На вході дозволяємо будь-які роздільники — пробіли,
    дужки, дефіси, плюси — і міжнародний префікс `+380` / `380`. Це
    означає, що `(063) 32-32-777`, `+380631234567`, `380 63 1234567`
    і `0631234567` всі нормалізуються до того самого значення, тож
    `remove`/`edit` працюватимуть незалежно від того, у якому вигляді
    користувач його ввів першого разу.
    """

    value: str

    @staticmethod
    def _normalize(raw: str) -> str:
        """Залишає тільки цифри; `380XXXXXXXXX` (12 цифр) → `0XXXXXXXXX`."""
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
    """Дата народження у форматі DD.MM.YYYY."""

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
    """Email з простою регексп-валідацією."""

    value: str

    def __init__(self, value: str) -> None:
        v = (value or "").strip()
        if not _EMAIL_RE.match(v):
            raise ValueError(f"Email '{value}' is invalid.")
        super().__init__(v)


class Address(Field):
    """Адреса. Мінімум 3 символи після обрізки пробілів."""

    value: str

    def __init__(self, value: str) -> None:
        v = (value or "").strip()
        if len(v) < 3:
            raise ValueError("Address must be at least 3 characters.")
        super().__init__(v)


_TAG_RE = re.compile(r"^[\w-]+$", re.UNICODE)


class Tag(Field):
    """Тег у вигляді slug'a (літери + цифри + `_` + `-`).

    Юнікодні літери теж дозволені (`\\w` у Python 3 за замовчуванням
    охоплює Cyrillic). Провідний `#` обрізається, регістр приводиться
    до нижнього. Це той самий тип, що використовують і контакти, і
    нотатки — щоб віртуальний модуль `tags` міг агрегувати з обох
    сторін без додаткової конверсії.
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
