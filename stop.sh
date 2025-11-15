#!/bin/bash

# Lucky Wheel Bot Stop Script
echo "🛑 Stopping Lucky Wheel Bot System..."

# Kill bot process
if pgrep -f "bot.py" > /dev/null; then
    echo "🤖 Stopping Telegram bot..."
    pkill -f "bot.py"
    sleep 2
    echo "✅ Bot stopped"
else
    echo "ℹ️ Bot was not running"
fi

# Kill web server process
if pgrep -f "web_server.py" > /dev/null; then
    echo "🌐 Stopping web server..."
    pkill -f "web_server.py"
    sleep 2
    echo "✅ Web server stopped"
else
    echo "ℹ️ Web server was not running"
fi

echo "🎉 All Lucky Wheel Bot services have been stopped!"