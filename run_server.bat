@echo off


:: Start Daphne server in a new terminal window
start "Daphne Server" cmd /k " daphne -b 0.0.0.0 -p 8000 MochaCafe.asgi:application"

:: Wait for 5 seconds (adjust if needed)

