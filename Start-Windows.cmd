@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 launch.py %*
) else (
  python launch.py %*
)
set "CW_EXIT=%errorlevel%"
if not "%CW_NO_PAUSE%"=="1" pause
exit /b %CW_EXIT%
