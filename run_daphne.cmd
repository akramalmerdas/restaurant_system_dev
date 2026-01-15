@echo off

REM Go to the folder where this script is located
cd /d "%~dp0"

REM Run python from the venv inside this folder
"%~dp0venv\Scripts\python.exe" -m daphne -b 127.0.0.1 -p 8000 MochaCafe.asgi:application
