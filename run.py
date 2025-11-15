#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lucky Wheel Telegram Bot dengan Mini App
Main Runner Script
"""

import os
import sys
import asyncio
import threading
import time
from subprocess import Popen, PIPE
import signal

class LuckyWheelBot:
    def __init__(self):
        self.bot_process = None
        self.web_server_process = None
        self.running = False

    def start_bot(self):
        """Start Telegram bot"""
        try:
            print("🤖 Starting Telegram Bot...")
            self.bot_process = Popen([sys.executable, '/workspace/bot.py'], 
                                   stdout=PIPE, stderr=PIPE, text=True)
            time.sleep(2)  # Give bot time to start
            if self.bot_process.poll() is None:
                print("✅ Bot started successfully!")
                return True
            else:
                print("❌ Bot failed to start")
                return False
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            return False

    def start_web_server(self):
        """Start web server for Mini App"""
        try:
            print("🌐 Starting Web Server...")
            self.web_server_process = Popen([sys.executable, '/workspace/web_server.py'], 
                                          stdout=PIPE, stderr=PIPE, text=True)
            time.sleep(2)  # Give server time to start
            if self.web_server_process.poll() is None:
                print("✅ Web Server started successfully!")
                return True
            else:
                print("❌ Web Server failed to start")
                return False
        except Exception as e:
            print(f"❌ Error starting web server: {e}")
            return False

    def start_all(self):
        """Start both bot and web server"""
        print("🎡 Lucky Wheel Bot dengan Mini App")
        print("=" * 50)
        
        # Start web server first
        if not self.start_web_server():
            print("❌ Failed to start web server. Exiting...")
            return False
        
        # Start bot
        if not self.start_bot():
            print("❌ Failed to start bot. Exiting...")
            return False
        
        self.running = True
        print("\n🎉 Lucky Wheel Bot System Started!")
        print("📱 Bot Token: 8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8")
        print("👤 Owner ID: 6395738130")
        print("👥 Group Chat: -1002917701297")
        print("📢 Channel: -1002502508906")
        print("\n💡 Ready to receive commands!")
        print("\n📋 Commands yang tersedia:")
        print("   /start - Aktivasi bot")
        print("   /menu - Buka menu game")
        print("\n🔄 Monitoring processes... (Ctrl+C to stop)")
        print("=" * 50)
        
        return True

    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Shutting down Lucky Wheel Bot System...")
        self.running = False
        
        if self.bot_process:
            print("🛑 Stopping Telegram Bot...")
            self.bot_process.terminate()
            self.bot_process.wait(timeout=5)
        
        if self.web_server_process:
            print("🛑 Stopping Web Server...")
            self.web_server_process.terminate()
            self.web_server_process.wait(timeout=5)
        
        print("✅ All processes stopped")

    def monitor_processes(self):
        """Monitor and restart failed processes"""
        while self.running:
            time.sleep(5)
            
            # Check bot process
            if self.bot_process and self.bot_process.poll() is not None:
                print("⚠️ Bot process died, restarting...")
                self.start_bot()
            
            # Check web server process
            if self.web_server_process and self.web_server_process.poll() is not None:
                print("⚠️ Web Server process died, restarting...")
                self.start_web_server()

    def run(self):
        """Main run function"""
        try:
            if self.start_all():
                self.monitor_processes()
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal...")
        finally:
            self.stop_all()

def main():
    """Main function"""
    lucky_wheel = LuckyWheelBot()
    lucky_wheel.run()

if __name__ == "__main__":
    main()