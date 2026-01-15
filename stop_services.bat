@echo off
echo Stopping MochaCafe services...
net stop "MochaCafe Proxy"
net stop "MochaCafe Worker"
net stop "MochaCafe Web"
echo.
echo Service status:
sc query "MochaCafe Web"
sc query "MochaCafe Worker"
sc query "MochaCafe Proxy"
pause
