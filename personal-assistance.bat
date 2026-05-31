@echo off
rem Convenience launcher for Personal Assistant on Windows.
rem
rem Resolves to the project root regardless of where it's called from,
rem prefers the local .venv if present, makes sure dependencies are
rem installed, clears the terminal, then hands off to
rem `python -m personal_assistant`.
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=py -3"
    ) else (
        set "PYTHON=python"
    )
)

%PYTHON% -c "import prompt_toolkit, rapidfuzz, rich" >nul 2>nul
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    %PYTHON% -m pip install -r requirements.txt
)

cls
%PYTHON% -m personal_assistant %*
