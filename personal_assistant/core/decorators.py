"""Input-error decorator.

Wraps handler functions; converts common exceptions raised by validators
or by argument unpacking into a friendly string for the user.
"""

from functools import wraps


def input_error(func):
    """Convert common exceptions into user-facing error strings.

    Catches:
        ValueError  — unpacking failure, validator errors (re-emits their text).
        KeyError    — lookup of a missing contact/note/tag.
        IndexError  — args[i] out of range.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            msg = str(e)
            if msg.startswith("not enough values to unpack"):
                return "Not enough arguments. Please provide all required information."
            return msg or "Invalid input. Please check your arguments."
        except KeyError as e:
            name = e.args[0] if e.args else "?"
            return f"Not found: '{name}'."
        except IndexError:
            return "Enter the argument for the command."

    return inner
