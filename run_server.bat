@echo off
cd /d E:\Django\MochaSystem\MochaCafe

:: Start Daphne server in a new terminal window
start "Daphne Server" cmd /k "call venv\Scripts\activate && daphne -b 0.0.0.0 -p 8000 MochaCafe.asgi:application"

:: Wait for 5 seconds (adjust if needed)
timeout /t 80 /nobreak >nul

:: Start Webview app in a new terminal window
start "Webview App" cmd /k "call venv\Scripts\activate && python desktop_app.py"
