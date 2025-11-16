#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lucky Wheel Bot - Improved Runner dengan Error Handling
"""

import os
import sys
import time
import socket
from subprocess import Popen, PIPE
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LuckyWheelBot:
    def __init__(self):
        self.web_server_process = None
        self.bot_process = None
        self.running = False

    def check_port(self, port):
        """Check if port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False

    def kill_process_on_port(self, port):
        """Kill process using specific port"""
        try:
            # Try to find and kill process using the port
            result = os.system(f"fuser -k {port}/tcp 2>/dev/null")
            if result == 0:
                logger.info(f"Killed process using port {port}")
                time.sleep(2)  # Wait for process to fully close
                return True
            else:
                # Alternative method using lsof if fuser not available
                os.system(f"lsof -ti:{port} | xargs kill -9 2>/dev/null")
                time.sleep(2)
                return True
        except Exception as e:
            logger.warning(f"Could not kill process on port {port}: {e}")
            return False

    def find_free_port(self, start_port=8081):
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + 10):
            if self.check_port(port):
                return port
        return None

    def start_web_server(self):
        """Start web server with better error handling"""
        logger.info("🌐 Starting Web Server...")
        
        # Find available port
        port = self.find_free_port()
        if not port:
            logger.error("❌ No available ports found!")
            return False
        
        # Set environment variable for port
        os.environ['MINI_APP_PORT'] = str(port)
        
        try:
            # Kill any existing process on this port
            self.kill_process_on_port(port)
            
            # Start web server
            self.web_server_process = Popen([
                sys.executable, os.path.join(os.getcwd(), "web_server.py")
            ], stdout=PIPE, stderr=PIPE, text=True)

            
            # Wait and check if started successfully
            time.sleep(3)
            
            if self.web_server_process.poll() is None:
                logger.info(f"✅ Web Server started successfully on port {port}")
                logger.info(f"🌐 Mini App URL: https://lootdungeon.online/luckywheel.html")
                os.environ['WEB_SERVER_URL'] = "https://lootdungeon.online"
                return True
            else:
                error_output = self.web_server_process.stderr.read()
                logger.error(f"❌ Web Server failed to start: {error_output}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting web server: {e}")
            return False

    def start_bot(self):
        """Start Telegram bot"""
        logger.info("🤖 Starting Telegram Bot...")
        
        try:
            # Update environment variables
            if 'MINI_APP_PORT' in os.environ:
                port = os.environ['MINI_APP_PORT']
                os.environ['WEB_SERVER_URL'] = f"http://localhost:{port}"
            
            self.bot_process = Popen([
                sys.executable, os.path.join(os.getcwd(), "bot.py")
            ], stdout=PIPE, stderr=PIPE, text=True)

            
            time.sleep(3)
            
            if self.bot_process.poll() is None:
                logger.info("✅ Bot started successfully!")
                return True
            else:
                error_output = self.bot_process.stderr.read()
                logger.error(f"❌ Bot failed to start: {error_output}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            return False

    def test_web_server(self, port):
        """Test if web server is responding"""
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/luckywheel.html", timeout=5)
            if response.status_code == 200 and "Lucky Wheel" in response.text:
                logger.info("✅ Web Server test passed")
                return True
            else:
                logger.warning("⚠️ Web Server responding but content mismatch")
                return False
        except Exception as e:
            logger.error(f"❌ Web Server test failed: {e}")
            return False

    def start_all(self):
        """Start both services with comprehensive error handling"""
        print("🎡 Lucky Wheel Bot - Enhanced Version")
        print("=" * 50)
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            logger.error("❌ Python 3.7+ required")
            return False
        
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check dependencies
        try:
            import telegram
            import requests
            logger.info("✅ Dependencies OK")
        except ImportError as e:
            logger.error(f"❌ Missing dependency: {e}")
            logger.info("💡 Install with: pip install python-telegram-bot==20.7 requests")
            return False
        
        # Start web server
        if not self.start_web_server():
            logger.error("❌ Cannot proceed without web server")
            return False
        
        # Get port for testing
        port = int(os.environ.get('MINI_APP_PORT', 8081))
        
        # Test web server
        if not self.test_web_server(port):
            logger.warning("⚠️ Web server test failed, but continuing...")
        
        # Start bot
        if not self.start_bot():
            logger.error("❌ Bot failed to start")
            return False
        
        self.running = True
        
        print("\n🎉 Lucky Wheel Bot System Started!")
        print("=" * 50)
        print(f"🤖 Bot Token: 8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8")
        print(f"👤 Owner ID: 6395738130")
        web_base = f"http://localhost:{port}"
        lucky_url = f"{web_base}/luckywheel.html"
        print(f"🌐 Web Server: {web_base}")
        print(f"🎡 Lucky Wheel: {lucky_url}")
        print("\n📱 Test di Telegram:")
        print("   1. Cari bot: @LuckyWheelRouletteBot")
        print("   2. Kirim: /start")
        print("   3. Kirim: /menu")
        print("\n🛑 Press Ctrl+C to stop")
        print("=" * 50)
        
        return True

    def stop_all(self):
        """Stop all processes gracefully"""
        logger.info("\n🛑 Shutting down...")
        self.running = False
        
        if self.bot_process:
            logger.info("🛑 Stopping Bot...")
            self.bot_process.terminate()
            try:
                self.bot_process.wait(timeout=5)
            except:
                self.bot_process.kill()
        
        if self.web_server_process:
            logger.info("🛑 Stopping Web Server...")
            self.web_server_process.terminate()
            try:
                self.web_server_process.wait(timeout=5)
            except:
                self.web_server_process.kill()
        
        logger.info("✅ All services stopped")

    def monitor_processes(self):
        """Monitor and restart failed processes"""
        while self.running:
            time.sleep(10)
            
            # Check bot process
            if self.bot_process and self.bot_process.poll() is not None:
                logger.warning("⚠️ Bot process died, restarting...")
                self.start_bot()
            
            # Check web server process
            if self.web_server_process and self.web_server_process.poll() is not None:
                logger.warning("⚠️ Web Server process died, restarting...")
                self.start_web_server()

def main():
    """Main function with enhanced error handling"""
    bot = LuckyWheelBot()
    
    try:
        if bot.start_all():
            bot.monitor_processes()
        else:
            print("❌ Failed to start Lucky Wheel Bot")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        bot.stop_all()

if __name__ == "__main__":
    main()
