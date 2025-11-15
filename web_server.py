#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MiniAppHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = os.path.join(BASE_DIR, "bot_database.db")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Serve Lucky Wheel HTML
            if path == '/luckywheel.html':
                self.serve_html_file(os.path.join(BASE_DIR, "luckywheel.html"))
            elif path == '/':
                # Redirect to lucky wheel
                self.send_response(302)
                self.send_header('Location', '/luckywheel.html')
                self.end_headers()
            else:
                self.send_error(404, "File not found")
                
        except Exception as e:
            logger.error(f"Error in GET request: {e}")
            self.send_error(500, "Internal server error")

    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if path == '/api/spin-result':
                self.handle_spin_result(post_data)
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
            self.send_error(500, "Internal server error")

    def serve_html_file(self, file_path):
        """Serve HTML file"""
        try:
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, "File not found")
        except Exception as e:
            logger.error(f"Error serving HTML file: {e}")
            self.send_error(500, "Error serving file")

    def handle_spin_result(self, post_data):
        """Handle spin result from Mini App"""
        try:
            # Parse JSON data
            data = json.loads(post_data)
            user_id = data.get('user_id')
            prize_type = data.get('prize_type')
            prize_value = data.get('prize_value')
            prize_emoji = data.get('prize_emoji', '')
            
            logger.info(f"Spin result received - User: {user_id}, Prize: {prize_type} x{prize_value}")
            
            # Save to database
            self.save_spin_result(user_id, prize_type, prize_value)
            
            # Send success response
            response = {
                'success': True,
                'message': 'Spin result saved successfully'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
            # Send notification to bot if possible
            self.notify_bot(user_id, prize_type, prize_value, prize_emoji)
            
        except Exception as e:
            logger.error(f"Error handling spin result: {e}")
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def save_spin_result(self, user_id, prize_type, prize_value):
        """Save spin result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add prize to user inventory
            if prize_type == "fizz_coin":
                cursor.execute('''
                    UPDATE users SET fizz_coin = fizz_coin + ?
                    WHERE user_id = ?
                ''', (prize_value, user_id))
            elif prize_type == "lucky_ticket":
                cursor.execute('''
                    UPDATE users SET lucky_ticket = lucky_ticket + ?
                    WHERE user_id = ?
                ''', (prize_value, user_id))
            elif prize_type == "hp_potion":
                cursor.execute('''
                    UPDATE users SET hp_potion = hp_potion + ?
                    WHERE user_id = ?
                ''', (prize_value, user_id))
            
            # Add to history
            cursor.execute('''
                INSERT INTO spin_history (user_id, prize_type, prize_value, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, prize_type, prize_value, datetime.now()))
            
            # Update last spin time
            cursor.execute('''
                UPDATE users SET last_spin = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Spin result saved to database for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving spin result to database: {e}")
            raise

    def notify_bot(self, user_id, prize_type, prize_value, prize_emoji):
        """Notify bot about spin result (placeholder - would integrate with bot API)"""
        try:
            # This would send a message to the bot or update the bot's database
            # For now, just log it
            logger.info(f"Notifying bot about spin result: User {user_id} got {prize_type} x{prize_value}")
            
            # You could implement:
            # 1. Direct database updates to bot's database
            # 2. Webhook calls to bot API
            # 3. Message queue for async communication
            
        except Exception as e:
            logger.error(f"Error notifying bot: {e}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def run_server(port=8080):
    """Run the web server"""
    try:
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, MiniAppHandler)
        logger.info(f"Mini App server running on port {port}")
        logger.info(f"Access Lucky Wheel at: http://localhost:{port}/luckywheel.html")
        
        print(f"""
🎡 Lucky Wheel Mini App Server Started!
========================================

📍 Server URL: http://localhost:{port}
🎯 Lucky Wheel: http://localhost:{port}/luckywheel.html

💡 Instructions:
1. Bot akan otomatis menjalankan di port yang sama
2. Mini App bisa diakses langsung dari browser untuk testing
3. Dari Telegram, klik tombol untuk membuka Mini App

⚡ Server ready untuk menerima koneksi...
        """)
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        httpd.shutdown()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get('MINI_APP_PORT', 8081))
    run_server(port)
