@echo off
REM wait-gateway.bat - fallback watcher after Windows-Start opens loading.html.
REM Slow USB drives can need tens of seconds before the gateway listens.
REM
REM Windows-Start opens Config Center immediately, so the ready path only
REM exits quietly. On timeout, reopen Config Center as a recovery hint.
REM Usage (called in background by Windows-Start.bat): wait-gateway.bat PORT CONFIG_PORT
REM Polls every 2 seconds, up to about 5 minutes.

set "PORT=%~1"
if "%PORT%"=="" set "PORT=18789"
set "CONFIG_PORT=%~2"
if "%CONFIG_PORT%"=="" set "CONFIG_PORT=18788"

set /a TRIES=0
:wait_loop
netstat -an | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 goto :ready
set /a TRIES+=1
if %TRIES% geq 150 goto :timeout
REM Use ping (not "timeout /t") for the ~2s delay: if a GNU coreutils "timeout"
REM is on PATH (Git/MSYS bin), it rejects "/t" and this poll becomes a busy-loop.
REM ping for the delay is PATH-robust and matches Windows-Start.bat's wait loop.
ping -n 3 127.0.0.1 >nul 2>&1
goto :wait_loop

:ready
exit /b 0

:timeout
start "" http://127.0.0.1:%CONFIG_PORT%/
exit /b 1
