@echo off
chcp 65001 >nul 2>&1
title Z-Claw - Portable AI Agent

echo.
echo   ========================================
echo     Z-Claw V1.0 - Portable AI Agent
echo   ========================================
echo.

set "zclaw_DIR=%~dp0"
set "APP_DIR=%zclaw_DIR%app"

REM Migration shim: rename old core-win to core for existing USB users
if exist "%APP_DIR%\core-win" if not exist "%APP_DIR%\core" ren "%APP_DIR%\core-win" core

set "CORE_DIR=%APP_DIR%\core"
set "DATA_DIR=%zclaw_DIR%data"
set "STATE_DIR=%DATA_DIR%\.openclaw"
set "NODE_DIR=%APP_DIR%\runtime\node-win-x64"
set "NODE_BIN=%NODE_DIR%\node.exe"
set "NPM_BIN=%NODE_DIR%\npm.cmd"

set "OPENCLAW_HOME=%DATA_DIR%"
set "OPENCLAW_STATE_DIR=%STATE_DIR%"
set "OPENCLAW_CONFIG_PATH=%STATE_DIR%\openclaw.json"
REM Z-Claw opens the local dashboard directly; disable mDNS discovery on Windows
REM to avoid OpenClaw/@homebridge ciao crashes during bonjour re-advertise.
set "OPENCLAW_DISABLE_BONJOUR=1"

REM Check runtime
if not exist "%NODE_BIN%" (
    echo   [ERROR] Node.js runtime not found
    echo   Please ensure app\runtime\node-win-x64 is complete
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('"%NODE_BIN%" --version') do set NODE_VER=%%v
echo   Node.js: %NODE_VER%
echo.

set "PATH=%NODE_DIR%;%NODE_DIR%\node_modules\.bin;%PATH%"

REM Init data directories
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%STATE_DIR%" mkdir "%STATE_DIR%"
if not exist "%DATA_DIR%\memory" mkdir "%DATA_DIR%\memory"
if not exist "%DATA_DIR%\backups" mkdir "%DATA_DIR%\backups"
if not exist "%DATA_DIR%\logs" mkdir "%DATA_DIR%\logs"

REM Startup cache acceleration.
REM portable-cache.mjs chooses a local-disk cache slot and redirects
REM .openclaw\browser there with a junction when possible.
REM Browser user data and V8 compile cache stay off the USB drive.
REM If this fails, startup continues with the cache on the USB drive.
for /f "usebackq tokens=1,* delims==" %%a in (`""%NODE_BIN%" "%zclaw_DIR%lib\portable-cache.mjs" "%STATE_DIR%" "%zclaw_DIR%" 2^>nul"`) do (
    if "%%a"=="zclaw_COMPILE_CACHE_DIR" set "NODE_COMPILE_CACHE=%%b"
    if "%%a"=="zclaw_CACHE_ROOT" set "zclaw_CACHE_ROOT=%%b"
)
if defined NODE_COMPILE_CACHE echo   Cache on local disk: %zclaw_CACHE_ROOT%

REM Default config (migrate legacy if present, otherwise create)
if not exist "%STATE_DIR%\openclaw.json" (
    if exist "%DATA_DIR%\config.json" (
        echo   Migrating legacy config...
        copy "%DATA_DIR%\config.json" "%STATE_DIR%\openclaw.json" >nul
        echo   Config migrated
    ) else (
        echo   First run - creating default config...
        (echo {"gateway":{"mode":"local","auth":{"token":"zclaw"}}})>"%STATE_DIR%\openclaw.json"
        echo   Config created
    )
    echo.
)

REM Check dependencies
REM Note: avoid unescaped parens inside this block -- cmd.exe treats ) as block-end.
if not exist "%CORE_DIR%\node_modules" (
    echo   ========================================
    echo   [WARN] node_modules not found
    echo   ========================================
    echo   This release should ship with deps pre-installed.
    echo   Falling back to npm install ^(USB drives may take 20+ minutes^).
    echo.
    echo   TIP: Re-download Z-Claw-portable-*.zip from GitHub releases,
    echo        which includes pre-installed deps ^(~200 MB^).
    echo.
    echo   File system: NTFS recommended. exFAT/FAT32 will be very slow.
    echo.
    cd /d "%CORE_DIR%"
    REM Keep npm cache inside the portable app instead of system APPDATA.
    set "npm_config_cache=%APP_DIR%\.npm-cache"
    call "%NPM_BIN%" install --registry=https://registry.npmmirror.com --ignore-scripts --no-audit --no-fund --omit=dev
    echo.
    echo   Dependencies installed!
    echo.
)

REM Intranet/self-hosted model fix: keep the configured model host(s) off any
REM corporate HTTP_PROXY/HTTPS_PROXY. OpenClaw routes ALL fetch through the env
REM proxy when it is set, which breaks calls to internal model endpoints
REM (e.g. http://10.x / 192.168.x / a machine-room IP). Add those hosts + loopback
REM to NO_PROXY so they connect directly. Silent no-op when no proxy/model is set.
for /f "usebackq tokens=1,* delims==" %%a in (`""%NODE_BIN%" "%zclaw_DIR%lib\resolve-no-proxy.mjs" "%STATE_DIR%\openclaw.json" 2^>nul"`) do (
    if "%%a"=="zclaw_NO_PROXY" set "NO_PROXY=%%b"
)
if defined NO_PROXY (
    set "no_proxy=%NO_PROXY%"
    REM Note: no unescaped parens in echo inside this IF block - cmd treats ) as block-end.
    echo   Direct-connect via NO_PROXY: %NO_PROXY%
)

REM Async update check (non-blocking, 5s timeout, silent failure)
REM Writes data\.openclaw\update-available.json if a newer version is on OSS.
REM Welcome.html / Config.html read this file and show a banner.
REM Version file lookup order: portable/OPENCLAW_VERSION (USB), then repo-root ../OPENCLAW_VERSION (dev)
set "VERSION_FILE=%zclaw_DIR%OPENCLAW_VERSION"
if not exist "%VERSION_FILE%" set "VERSION_FILE=%zclaw_DIR%..\OPENCLAW_VERSION"
if exist "%VERSION_FILE%" (
    start /B "" "%NODE_BIN%" "%zclaw_DIR%lib\check-update.mjs" "%VERSION_FILE%" "%STATE_DIR%" >nul 2>&1
)


REM Auto-install WeChat plugin if available
set "WECHAT_PLUGIN_SRC=%APP_DIR%\extensions\openclaw-weixin"
set "WECHAT_PLUGIN_DST=%USERPROFILE%\.openclaw\extensions\openclaw-weixin"
if exist "%WECHAT_PLUGIN_SRC%\openclaw.plugin.json" (
    if not exist "%WECHAT_PLUGIN_DST%\openclaw.plugin.json" (
        echo   Installing WeChat plugin...
        mkdir "%USERPROFILE%\.openclaw\extensions" 2>nul
        xcopy /s /e /q /y "%WECHAT_PLUGIN_SRC%" "%WECHAT_PLUGIN_DST%\" >nul
        echo   WeChat plugin installed!
        echo.
    )
)

REM Start Config Server in background
echo   Starting Config Center on port 18788...
set "CONFIG_SERVER=%zclaw_DIR%config-server"
set "RUNTIME_JSON=%STATE_DIR%\runtime.json"
del "%RUNTIME_JSON%" >nul 2>&1
start /B "" "%NODE_BIN%" "%CONFIG_SERVER%\server.js" >nul 2>&1

REM Wait for Config Server with polling instead of a fixed delay.
REM It writes runtime.json with the actual fallback port when ready.
set /a CFG_TRIES=0
:wait_config
if exist "%RUNTIME_JSON%" goto :config_ready
set /a CFG_TRIES+=1
if %CFG_TRIES% geq 20 goto :config_ready
ping -n 1 -w 300 127.0.0.1 >nul 2>&1
goto :wait_config
:config_ready
set "CONFIG_PORT=18788"
if exist "%RUNTIME_JSON%" (
    for /f "usebackq tokens=*" %%p in (`powershell -NoProfile -Command "try { (Get-Content -Raw '%RUNTIME_JSON%' | ConvertFrom-Json).configServerPort } catch {}" 2^>nul`) do set "CONFIG_PORT=%%p"
)
echo   Config Center port: %CONFIG_PORT%

REM Find available gateway port after Config Center has bound its port.
set PORT=18789
:check_port
netstat -an | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo   Port %PORT% in use, trying next...
    set /a PORT+=1
    if %PORT% gtr 18799 (
        echo   No available port 18789-18799
        pause
        exit /b 1
    )
    goto :check_port
)

echo   Starting OpenClaw on port %PORT%...
echo.

REM Do not open Dashboard before the gateway is ready.
REM Slow USB drives may need tens of seconds to stage bundled deps.
REM Open the local startup page now, and always open Config Center too.
REM Config Center lets users change models, recharge/get keys, and connect channels.

REM Open startup page with the gateway port and token in the query string.
echo   Opening startup screen...
set "LOADING_PATH=%zclaw_DIR%lib\loading.html"
set "LOADING_URL=file:///%LOADING_PATH:\=/%?port=%PORT%&token=zclaw"
start "" "%LOADING_URL%"

echo   Opening Config Center...
start "" http://127.0.0.1:%CONFIG_PORT%/

REM Fallback watcher: if the startup page cannot poll from file URLs,
REM keep polling and reopen Config Center after the gateway is ready.
start /B "" cmd /c ""%zclaw_DIR%lib\wait-gateway.bat" %PORT% %CONFIG_PORT%"

REM Prewarm gateway in the background after it becomes ready.
start /B "" "%NODE_BIN%" "%zclaw_DIR%lib\prewarm.mjs" %PORT% zclaw >nul 2>&1

echo.
echo   ========================================
echo   Starting OpenClaw Gateway on port %PORT%...
echo   First run on a USB drive may take 30-90 seconds
echo   (unpacking bundled components). Please wait;
echo   Config Center is open for model, key, recharge, and channel setup.
echo   DO NOT close this window while using Z-Claw!
echo   ========================================
echo.

cd /d "%CORE_DIR%"
set "OPENCLAW_MJS=%CORE_DIR%\node_modules\openclaw\openclaw.mjs"
"%NODE_BIN%" "%OPENCLAW_MJS%" gateway run --allow-unconfigured --force --port %PORT%
set "GW_EXIT=%errorlevel%"

echo.
if not "%GW_EXIT%"=="0" if not "%GW_EXIT%"=="-1073741510" (
    echo   OpenClaw exited unexpectedly ^(code %GW_EXIT%^)
)
echo   OpenClaw stopped.
pause
