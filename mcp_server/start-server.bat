@echo off
REM Start MCP Server with Enhanced Monitoring (Windows version)
REM This script starts the server and provides instructions for testing

echo 🚀 Starting MCP Development Assistant Server with Enhanced Monitoring
echo ==============================================================

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Check if Redis is running
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo ⚠️  Redis not detected. Please start Redis manually:
    echo    - Install Redis for Windows
    echo    - Or use Docker: docker run -d -p 6379:6379 redis:alpine
    echo    - Or use WSL with Redis
    pause
    exit /b 1
)

echo ✅ Redis is running

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo 📦 Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

echo 📊 Starting MCP Server with monitoring...
echo    - REST API: http://localhost:8000
echo    - WebSocket: ws://localhost:8000/mcp
echo    - Health: http://localhost:8000/admin/health
echo    - Analytics: http://localhost:8000/admin/analytics/stats

echo.
echo 📋 Quick Test Commands:
echo 1. Health Check:
echo    curl http://localhost:8000/
echo.
echo 2. List Tools:
echo    curl -H "X-API-Key: dev-test-key" http://localhost:8000/tools
echo.
echo 3. Execute Tool:
echo    curl -X POST http://localhost:8000/tools/execute ^
echo      -H "X-API-Key: dev-test-key" ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"tool_name\": \"scan_codebase\", \"arguments\": {\"query\": \"python\"}}"
echo.
echo 4. Verify Tool Calls:
echo    curl -H "X-API-Key: dev-test-key" http://localhost:8000/verify/tools
echo.
echo 5. Run Test Suite:
echo    python ..\test_mcp_server.py
echo.
echo 📊 Monitoring Features:
echo    - All tool calls are logged with IDE detection
echo    - Real-time analytics available at /admin/analytics/*
echo    - Verification endpoint shows exactly which tools were called
echo    - Logs stored in logs\mcp-server.log
echo.
echo 🛑 To stop the server, press Ctrl+C

REM Start the server
python server.py
