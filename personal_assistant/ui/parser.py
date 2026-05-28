"""Parse user input into (command_name, args).

shlex handles quoted strings (`"two words"` → one arg). Falls back to
plain split on an unmatched quote so REPL never crashes on malformed
input.
"""

import shlex


def parse_input(line: str) -> tuple[str, list[str]]:
    line = line.strip()
    if not line:
        return "", []
    try:
        tokens = shlex.split(line)
    except ValueError:
        tokens = line.split()
    cmd = tokens[0].lower()
    args = tokens[1:]
    return cmd, args