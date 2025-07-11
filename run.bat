@echo off
:: Navigate to your Django project directory
cd /d E:\Django\MochaSystem\MochaCafe

:: Activate the virtual environment
call venv\Scripts\activate

:: Run Daphne server on all interfaces, port 8000
daphne -b 0.0.0.0 -p 8000 MochaCafe.asgi:application

:: Keep the window open after execution
pause