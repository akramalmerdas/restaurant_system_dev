@echo off
cd /d E:\Django\MochaSystem\MochaCafe

:: Activate virtual environment (adjust if needed)
call venv\Scripts\activate

:: Run Django development server
py manage.py runserver 0.0.0.0:8000

pause
