@echo off
cd /d E:\Django\MochaSystem\MochaCafe
call venv\Scripts\activate.bat

:loop
python print_orders.py
timeout /t 10 >nul
goto loop
