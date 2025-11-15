#!/bin/bash

# Lucky Wheel Bot Startup Script
echo "🎡 Lucky Wheel Telegram Bot - Quick Start"
echo "========================================"

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo "✅ $1 is running"
        return 0
    else
        echo "❌ $1 is not running"
        return 1
    fi
}

# Function to kill process
kill_process() {
    pkill -f "$1" 2>/dev/null
    sleep 2
}

echo "🚀 Starting Lucky Wheel Bot System..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
kill_process "web_server.py"
kill_process "bot.py"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Check dependencies
echo "📦 Checking dependencies..."
if python3 -c "import telegram, requests" 2>/dev/null; then
    echo "✅ Dependencies OK"
else
    echo "❌ Dependencies missing. Installing..."
    pip3 install python-telegram-bot==20.7 requests
fi

# Start web server in background
echo "🌐 Starting web server..."
nohup python3 /workspace/web_server.py > /workspace/web_server.log 2>&1 &
sleep 3

if check_process "web_server.py"; then
    echo "✅ Web server started successfully"
else
    echo "❌ Web server failed to start"
    exit 1
fi

# Start bot in background
echo "🤖 Starting Telegram bot..."
nohup python3 /workspace/bot.py > /workspace/bot.log 2>&1 &
sleep 3

if check_process "bot.py"; then
    echo "✅ Bot started successfully"
else
    echo "❌ Bot failed to start"
    exit 1
fi

echo ""
echo "🎉 Lucky Wheel Bot System Started Successfully!"
echo "==============================================="
echo ""
echo "📊 Status:"
check_process "web_server.py"
check_process "bot.py"
echo ""
echo "🔗 URLs:"
echo "   Bot Token: 8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
echo "   Web Server: http://localhost:8080"
echo "   Lucky Wheel: http://localhost:8080/luckywheel.html"
echo ""
echo "📱 Telegram Commands:"
echo "   /start - Activate bot"
echo "   /menu - Open game menu"
echo ""
echo "📁 Logs:"
echo "   Web Server: /workspace/web_server.log"
echo "   Bot: /workspace/bot.log"
echo ""
echo "🛑 To stop: bash /workspace/stop.sh"
echo ""

# Keep script running
echo "Press Ctrl+C to stop all services..."
trap 'echo ""; echo "🛑 Stopping services..."; kill_process "bot.py"; kill_process "web_server.py"; echo "✅ All services stopped"; exit 0' INT

while true; do
    sleep 10
    # Health check
    if ! check_process "web_server.py" >/dev/null 2>&1; then
        echo "⚠️ Web server died, restarting..."
        nohup python3 /workspace/web_server.py > /workspace/web_server.log 2>&1 &
    fi
    if ! check_process "bot.py" >/dev/null 2>&1; then
        echo "⚠️ Bot died, restarting..."
        nohup python3 /workspace/bot.py > /workspace/bot.log 2>&1 &
    fi
done