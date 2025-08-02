#!/bin/bash
# Start MCP Server with Enhanced Monitoring
# This script starts the server and provides instructions for testing

echo "🚀 Starting MCP Development Assistant Server with Enhanced Monitoring"
echo "=============================================================="

# Create necessary directories
mkdir -p logs
mkdir -p data

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis not detected. Starting Redis..."
    # For Windows with Redis installed
    if command -v redis-server &> /dev/null; then
        redis-server &
    else
        echo "❌ Redis not found. Please install and start Redis first:"
        echo "   - Windows: Download from https://redis.io/download"
        echo "   - Or use Docker: docker run -d -p 6379:6379 redis:alpine"
        exit 1
    fi
fi

echo "✅ Redis is running"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..."
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    pip install -r requirements.txt
else
    source venv/bin/activate  # For Windows: venv\Scripts\activate
fi

echo "📊 Starting MCP Server with monitoring..."
echo "   - REST API: http://localhost:8000"
echo "   - WebSocket: ws://localhost:8000/mcp"
echo "   - Health: http://localhost:8000/admin/health"
echo "   - Analytics: http://localhost:8000/admin/analytics/stats"

# Start the server
python server.py &
SERVER_PID=$!

echo "🎯 Server started with PID: $SERVER_PID"
echo ""
echo "📋 Quick Test Commands:"
echo "1. Health Check:"
echo "   curl http://localhost:8000/"
echo ""
echo "2. List Tools:"
echo "   curl -H 'X-API-Key: dev-test-key' http://localhost:8000/tools"
echo ""
echo "3. Execute Tool:"
echo "   curl -X POST http://localhost:8000/tools/execute \\"
echo "     -H 'X-API-Key: dev-test-key' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tool_name\": \"scan_codebase\", \"arguments\": {\"query\": \"python\"}}'"
echo ""
echo "4. Verify Tool Calls:"
echo "   curl -H 'X-API-Key: dev-test-key' http://localhost:8000/verify/tools"
echo ""
echo "5. Run Test Suite:"
echo "   python ../test_mcp_server.py"
echo ""
echo "📊 Monitoring Features:"
echo "   - All tool calls are logged with IDE detection"
echo "   - Real-time analytics available at /admin/analytics/*"
echo "   - Verification endpoint shows exactly which tools were called"
echo "   - Logs stored in logs/mcp-server.log"
echo ""
echo "🛑 To stop the server, press Ctrl+C or kill $SERVER_PID"

# Wait for the server process
wait $SERVER_PID
