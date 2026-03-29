@echo off
:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run Daphne server on all interfaces, port 8000
venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 MochaCafe.asgi:application

:: Keep the window open after execution
pause