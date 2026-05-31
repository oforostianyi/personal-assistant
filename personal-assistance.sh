#!/usr/bin/env bash
# Convenience launcher for Personal Assistant on Linux and macOS.
#
# Resolves to the project root regardless of where it's called from,
# prefers the local .venv if present, makes sure dependencies are
# installed, clears the terminal, then hands off to
# `python -m personal_assistant`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

if ! "$PYTHON" -c "import prompt_toolkit, rapidfuzz, rich" 2>/dev/null; then
    echo "Installing dependencies from requirements.txt..."
    "$PYTHON" -m pip install -r requirements.txt
fi

if command -v clear >/dev/null 2>&1; then
    clear
else
    printf '\033c'
fi

exec "$PYTHON" -m personal_assistant "$@"
