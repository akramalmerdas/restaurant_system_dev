@echo off
echo MochaCafe Service Status
echo ========================
echo.
sc query "MochaCafe Web"
echo.
sc query "MochaCafe Worker"
echo.
sc query "MochaCafe Proxy"
echo.
echo Recent log entries:
echo -------------------
echo Web Service (last 10 lines):
powershell "Get-Content 'D:\\Newfolder2\\restaurant_system_dev\\logs\\web_output.log' -Tail 10 -ErrorAction SilentlyContinue"
echo.
echo Worker Service (last 10 lines):
powershell "Get-Content 'D:\\Newfolder2\\restaurant_system_dev\\logs\\worker_output.log' -Tail 10 -ErrorAction SilentlyContinue"
echo.
echo Caddy Proxy (last 10 lines):
powershell "Get-Content 'D:\\Newfolder2\\restaurant_system_dev\\logs\\caddy_output.log' -Tail 10 -ErrorAction SilentlyContinue"
pause
