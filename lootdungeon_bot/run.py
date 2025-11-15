"""
Main runner for LootDungeon Bot System
Runs both Telegram bot and web server
"""
import threading
import time
import os
from bot import main as bot_main
from web_app import app as flask_app

def run_bot():
    """Run the Telegram bot"""
    print("🤖 Starting Telegram Bot...")
    bot_main()

def run_web():
    """Run the Flask web server"""
    print("🌐 Starting Web Server...")
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    print("🚀 Starting LootDungeon System...")
    print("=" * 50)
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    print("✅ Web server started on port 5000")
    print("📱 Telegram bot is starting...")
    print("=" * 50)
    
    # Give web server a moment to start
    time.sleep(2)
    
    # Start bot in main thread
    run_bot()