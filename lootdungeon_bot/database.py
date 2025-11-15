"""
Database management for LootDungeon Bot
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config import DATABASE_PATH, LUCKY_WHEEL_PRIZES

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tickets INTEGER DEFAULT 10,
                coins INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_type TEXT,
                item_name TEXT,
                emoji TEXT,
                quantity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )
        ''')
        
        # Spin history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prize_type TEXT,
                prize_name TEXT,
                prize_emoji TEXT,
                quantity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_player(self, user_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None) -> bool:
        """Get existing player or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if player exists
        cursor.execute('SELECT user_id FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return False  # Player already exists
        
        # Create new player
        cursor.execute('''
            INSERT INTO players (user_id, username, first_name, last_name, tickets)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, 10))
        
        conn.commit()
        conn.close()
        return True  # New player created
    
    def get_player(self, user_id: int) -> Optional[Dict]:
        """Get player information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, tickets, coins, registered_at
            FROM players WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'tickets': result[4],
                'coins': result[5],
                'registered_at': result[6]
            }
        return None
    
    def get_player_items(self, user_id: int) -> List[Dict]:
        """Get all items for a player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT item_type, item_name, emoji, quantity, created_at
            FROM items WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'item_type': row[0],
            'item_name': row[1], 
            'emoji': row[2],
            'quantity': row[3],
            'created_at': row[4]
        } for row in results]
    
    def add_item(self, user_id: int, item_type: str, item_name: str, 
                emoji: str, quantity: int) -> bool:
        """Add item to player inventory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if item type already exists
        cursor.execute('''
            SELECT quantity FROM items WHERE user_id = ? AND item_type = ?
        ''', (user_id, item_type))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            new_quantity = existing[0] + quantity
            cursor.execute('''
                UPDATE items SET quantity = ? WHERE user_id = ? AND item_type = ?
            ''', (new_quantity, user_id, item_type))
        else:
            # Add new item
            cursor.execute('''
                INSERT INTO items (user_id, item_type, item_name, emoji, quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, item_type, item_name, emoji, quantity))
        
        conn.commit()
        conn.close()
        return True
    
    def use_tickets(self, user_id: int, amount: int) -> bool:
        """Use tickets from player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT tickets FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        current_tickets = result[0]
        if current_tickets < amount:
            conn.close()
            return False
        
        new_tickets = current_tickets - amount
        cursor.execute('UPDATE players SET tickets = ? WHERE user_id = ?', 
                      (new_tickets, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def add_tickets(self, user_id: int, amount: int):
        """Add tickets to player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT tickets FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            new_tickets = result[0] + amount
            cursor.execute('UPDATE players SET tickets = ? WHERE user_id = ?', 
                          (new_tickets, user_id))
            conn.commit()
        
        conn.close()
    
    def add_coins(self, user_id: int, amount: int):
        """Add coins to player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT coins FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            new_coins = result[0] + amount
            cursor.execute('UPDATE players SET coins = ? WHERE user_id = ?', 
                          (new_coins, user_id))
            conn.commit()
        
        conn.close()
    
    def log_spin(self, user_id: int, prize_type: str, prize_name: str, 
                prize_emoji: str, quantity: int):
        """Log spin result to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO spin_history (user_id, prize_type, prize_name, prize_emoji, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, prize_type, prize_name, prize_emoji, quantity))
        
        conn.commit()
        conn.close()
    
    def transfer_item(self, from_user_id: int, to_user_id: int, item_type: str, 
                     quantity: int) -> bool:
        """Transfer item between players"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if sender has enough quantity
            cursor.execute('''
                SELECT quantity FROM items WHERE user_id = ? AND item_type = ?
            ''', (from_user_id, item_type))
            
            sender_item = cursor.fetchone()
            if not sender_item or sender_item[0] < quantity:
                conn.close()
                return False
            
            # Reduce sender quantity
            new_sender_quantity = sender_item[0] - quantity
            if new_sender_quantity == 0:
                cursor.execute('''
                    DELETE FROM items WHERE user_id = ? AND item_type = ?
                ''', (from_user_id, item_type))
            else:
                cursor.execute('''
                    UPDATE items SET quantity = ? WHERE user_id = ? AND item_type = ?
                ''', (new_sender_quantity, from_user_id, item_type))
            
            # Add to receiver
            cursor.execute('''
                SELECT quantity FROM items WHERE user_id = ? AND item_type = ?
            ''', (to_user_id, item_type))
            
            receiver_item = cursor.fetchone()
            if receiver_item:
                new_receiver_quantity = receiver_item[0] + quantity
                cursor.execute('''
                    UPDATE items SET quantity = ? WHERE user_id = ? AND item_type = ?
                ''', (new_receiver_quantity, to_user_id, item_type))
            else:
                # Get item details
                prize_info = LUCKY_WHEEL_PRIZES[item_type]
                cursor.execute('''
                    INSERT INTO items (user_id, item_type, item_name, emoji, quantity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (to_user_id, item_type, prize_info['name'], 
                      prize_info['emoji'], quantity))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Transfer error: {e}")
            conn.close()
            return False