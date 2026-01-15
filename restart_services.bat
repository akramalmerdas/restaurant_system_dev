@echo off
echo Restarting MochaCafe services...
net stop "MochaCafe Proxy"
net stop "MochaCafe Worker"
net stop "MochaCafe Web"
timeout /t 3 /nobreak >nul
net start "MochaCafe Web"
net start "MochaCafe Worker"
net start "MochaCafe Proxy"
echo.
echo Service status:
sc query "MochaCafe Web"
sc query "MochaCafe Worker"
sc query "MochaCafe Proxy"
pause
