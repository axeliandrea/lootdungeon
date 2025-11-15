#!/bin/bash

# Lucky Wheel Bot Setup Script
echo "🎡 Lucky Wheel Telegram Bot Setup"
echo "================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install python-telegram-bot==20.7 requests

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x /workspace/run.py
chmod +x /workspace/bot.py
chmod +x /workspace/web_server.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the bot, run:"
echo "   python3 /workspace/run.py"
echo ""
echo "📋 Available commands in Telegram:"
echo "   /start - Aktivasi bot"
echo "   /menu - Buka menu game"
echo ""
echo "🔧 Configuration:"
echo "   Bot Token: 8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
echo "   Owner ID: 6395738130"
echo "   Group Chat ID: -1002917701297"
echo "   Channel ID: -1002502508906"
echo ""
echo "💡 The bot will automatically:"
echo "   1. Start web server on port 8080"
echo "   2. Start Telegram bot"
echo "   3. Provide Mini App Lucky Wheel"
echo "   4. Handle inventory and database"