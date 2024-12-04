@echo off

where python.exe > NUL 2>&1
if %errorlevel% neq 0 (
  echo Python not found! Please install Python and ensure it's in your PATH.
  echo See https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

cd src
python -m main
pause
