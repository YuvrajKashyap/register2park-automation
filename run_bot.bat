@echo off
setlocal
cd /d "%~dp0"
python main.py
set "EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %EXIT_CODE%
