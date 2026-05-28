"""Base class for any record field.

Field is a minimal container for a value with equality and string
representation. Concrete fields (Name, Phone, Email, Tag, ...) live
in their respective modules (e.g. contacts/fields.py).
"""


class Field:
    """Base class for record fields."""

    def __init__(self, value: object) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Field):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.value))