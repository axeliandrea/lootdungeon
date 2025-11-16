#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lucky Wheel Bot - Runner (Fixed Version)
Sinkron dengan bot.py → WEB_SERVER_URL = https://axeliandrea.github.io/lootdungeon
"""

import os
import sys
import time
import socket
from subprocess import Popen, PIPE
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL Mini App (HARUS SAMA DENGAN bot.py)
STATIC_WEB_URL = "https://axeliandrea.github.io/lootdungeon"


class LuckyWheelBot:
    def __init__(self):
        self.web_server_process = None
        self.bot_process = None
        self.running = False

    def start_web_server(self):
        """
        Start web_server.py tanpa localhost port.
        Karena Mini App sudah hosted di GitHub Pages.
        """
        logger.info("🌐 Starting Web Server (GitHub Pages Mode)...")

        # Set URL environment untuk bot.py
        os.environ['WEB_SERVER_URL'] = STATIC_WEB_URL
        logger.info(f"🌐 Mini App URL set to: {STATIC_WEB_URL}")

        try:
            # Jalankan web server (jika dibutuhkan)
            self.web_server_process = Popen([
                sys.executable, os.path.join(os.getcwd(), "web_server.py")
            ], stdout=PIPE, stderr=PIPE, text=True)

            time.sleep(2)

            if self.web_server_process.poll() is None:
                logger.info(f"✅ Web Server (static) running")
                return True

            error_msg = self.web_server_process.stderr.read()
            logger.error(f"❌ Web Server error: {error_msg}")
            return False

        except Exception as e:
            logger.error(f"❌ Error starting web server: {e}")
            return False

    def start_bot(self):
        """Start Telegram bot"""
        logger.info("🤖 Starting Telegram Bot...")

        # Kirim URL environment ke bot
        os.environ['WEB_SERVER_URL'] = STATIC_WEB_URL

        try:
            self.bot_process = Popen([
                sys.executable, os.path.join(os.getcwd(), "bot.py")
            ], stdout=PIPE, stderr=PIPE, text=True)

            time.sleep(3)

            if self.bot_process.poll() is None:
                logger.info("✅ Bot started successfully!")
                return True

            error_msg = self.bot_process.stderr.read()
            logger.error(f"❌ Bot failed to start: {error_msg}")
            return False

        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            return False

    def start_all(self):
        """Menjalankan seluruh sistem"""
        print("🎡 Lucky Wheel Bot Runner (GitHub Pages Mode)")
        print("=" * 50)

        # Start web server (static)
        if not self.start_web_server():
            logger.error("❌ Web Server failed")
            return False

        # Start bot
        if not self.start_bot():
            logger.error("❌ Bot failed")
            return False

        self.running = True

        print("\n🎉 Lucky Wheel System Started!")
        print("=" * 50)
        print("🤖 Bot Token: (disembunyikan)")
        print("🌐 Mini App URL:", STATIC_WEB_URL)
        print("🎡 Lucky Wheel:", STATIC_WEB_URL + "/luckywheel.html")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 50)

        return True

    def stop_all(self):
        """Stop all processes"""
        logger.info("\n🛑 Stopping all services...")
        self.running = False

        if self.bot_process:
            self.bot_process.terminate()
            try:
                self.bot_process.wait(timeout=5)
            except:
                self.bot_process.kill()

        if self.web_server_process:
            self.web_server_process.terminate()
            try:
                self.web_server_process.wait(timeout=5)
            except:
                self.web_server_process.kill()

        logger.info("✅ All services stopped")


def main():
    bot = LuckyWheelBot()

    try:
        if bot.start_all():
            while True:
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

    finally:
        bot.stop_all()


if __name__ == "__main__":
    main()
