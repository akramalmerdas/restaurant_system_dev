@echo off
echo Starting MochaCafe services...
net start "MochaCafe Web"
net start "MochaCafe Worker"
net start "MochaCafe Proxy"
echo.
echo Service status:
sc query "MochaCafe Web"
sc query "MochaCafe Worker"
sc query "MochaCafe Proxy"
pause
