@echo off
chcp 65001 >nul 2>&1
title Z-Claw - Local / Intranet Model Setup
setlocal

set "zclaw_DIR=%~dp0"
set "NODE_BIN=%zclaw_DIR%app\runtime\node-win-x64\node.exe"
set "CONFIG_PATH=%zclaw_DIR%data\.openclaw\openclaw.json"

if not exist "%NODE_BIN%" (
    echo   [ERROR] Node runtime not found.
    echo   Put this file inside your Z-Claw folder, next to Windows-Start.bat, then run again.
    echo.
    pause
    exit /b 1
)

"%NODE_BIN%" "%zclaw_DIR%lib\setup-local-model.mjs" "%CONFIG_PATH%"

echo.
pause
