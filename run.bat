@echo off
:: Navigate to your Django project directory
cd /d E:\Django\MochaSystem\MochaCafe

:: Run Django server using the venv Python executable
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

:: Keep the window open after it stops (e.g., error or exit)
pause
