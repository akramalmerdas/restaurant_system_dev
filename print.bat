@echo off
title Orders Processing Script
cd /d E:\Django\MochaSystem\MochaCafe

:: Activate virtual environment (if needed)
call venv\Scripts\activate

:loop
echo Starting orders script...
python print_orders.py
echo Script crashed or stopped. Restarting...
timeout /t 5 /nobreak >nul
goto loop
