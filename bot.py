#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lucky Wheel Bot - FIXED VERSION
Solusi untuk masalah hadiah tidak masuk ke bag
"""

import asyncio
import logging
import sqlite3
import json
import hashlib
from datetime import datetime
from urllib.parse import urljoin

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Konfigurasi Bot
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
OWNER_ID = 6395738130
GROUP_CHAT_ID = -1002917701297
CHANNEL_ID = -1002502508906

# URL untuk Mini App (GitHub Pages)
WEB_SERVER_URL = "https://axeliandrea.github.io/lootdungeon"

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Enable detailed logging untuk debugging
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inisialisasi database dengan tabel yang diperlukan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel users untuk menyimpan data user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registered BOOLEAN DEFAULT FALSE,
                join_group BOOLEAN DEFAULT FALSE,
                join_channel BOOLEAN DEFAULT FALSE,
                fizz_coin INTEGER DEFAULT 0,
                lucky_ticket INTEGER DEFAULT 3,
                hp_potion INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_spin TIMESTAMP
            )
        ''')
        
        # Tabel spin_history untuk menyimpan riwayat spin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prize_type TEXT,
                prize_value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabel prizes untuk konfigurasi hadiah
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prizes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prize_type TEXT,
                prize_value INTEGER,
                prize_name TEXT,
                emoji TEXT
            )
        ''')
        
        # Insert default prizes jika belum ada
        default_prizes = [
            ("fizz_coin", 100, "100 Fizz Coin", "💰 1x"),
            ("fizz_coin", 300, "300 Fizz Coin", "💰 3x"),
            ("fizz_coin", 500, "500 Fizz Coin", "💰 5x"),
            ("lucky_ticket", 1, "1 Lucky Ticket", "🎫 1x"),
            ("lucky_ticket", 3, "3 Lucky Ticket", "🎫 3x"),
            ("lucky_ticket", 5, "5 Lucky Ticket", "🎫 5x"),
            ("hp_potion", 5, "5 HP Potion", "🧪 5x"),
            ("zonk", 0, "Zonk", "☠️")
        ]
        
        for prize in default_prizes:
            cursor.execute('''
                INSERT OR IGNORE INTO prizes (prize_type, prize_value, prize_name, emoji)
                VALUES (?, ?, ?, ?)
            ''', prize)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
    
    def get_user(self, user_id):
        """Ambil data user dari database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_user(self, user_id, username, first_name):
        """Buat user baru jika belum ada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()
        logger.info(f"✅ User {user_id} created/verified")
    
    def update_user(self, user_id, **kwargs):
        """Update data user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        logger.info(f"✅ User {user_id} updated: {kwargs}")
    
    def get_user_inventory(self, user_id):
        """Ambil inventory user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT fizz_coin, lucky_ticket, hp_potion FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "fizz_coin": result[0],
                "lucky_ticket": result[1], 
                "hp_potion": result[2]
            }
        return None
    
    def deduct_ticket(self, user_id):
        """Kurangi lucky ticket"""
        if user_id == OWNER_ID:
            logger.info("👑 Owner detected, skipping ticket deduction")
            return True
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cek apakah user punya ticket
        cursor.execute("SELECT lucky_ticket FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            cursor.execute("UPDATE users SET lucky_ticket = lucky_ticket - 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Ticket deducted for user {user_id}")
            return True
        else:
            conn.close()
            logger.warning(f"❌ User {user_id} has no tickets")
            return False
    
    def add_prize(self, user_id, prize_type, prize_value):
        """Tambah hadiah ke inventory user"""
        try:
            logger.info(f"🎁 Adding prize: User {user_id}, Type: {prize_type}, Value: {prize_value}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validasi prize_type
            valid_types = ["fizz_coin", "lucky_ticket", "hp_potion"]
            if prize_type not in valid_types:
                logger.error(f"❌ Invalid prize type: {prize_type}")
                return False
            
            # Update inventory berdasarkan tipe hadiah
            if prize_type == "fizz_coin":
                cursor.execute("UPDATE users SET fizz_coin = fizz_coin + ? WHERE user_id = ?", 
                              (prize_value, user_id))
            elif prize_type == "lucky_ticket":
                cursor.execute("UPDATE users SET lucky_ticket = lucky_ticket + ? WHERE user_id = ?", 
                              (prize_value, user_id))
            elif prize_type == "hp_potion":
                cursor.execute("UPDATE users SET hp_potion = hp_potion + ? WHERE user_id = ?", 
                              (prize_value, user_id))
            
            # Simpan ke spin_history
            cursor.execute("""
                INSERT INTO spin_history (user_id, prize_type, prize_value) 
                VALUES (?, ?, ?)
            """, (user_id, prize_type, prize_value))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Prize added successfully to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding prize: {e}")
            return False
    
    def get_spin_history(self, user_id, limit=10):
        """Ambil riwayat spin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT prize_type, prize_value, created_at 
            FROM spin_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return history

# Inisialisasi database manager
db = DatabaseManager()

async def check_membership(user_id, bot):
    """Cek apakah user sudah join group dan channel"""
    try:
        # Cek group membership
        try:
            group_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
            in_group = group_member.status in ["member", "administrator", "creator"]
        except:
            in_group = False
        
        # Cek channel membership
        try:
            channel_member = await bot.get_chat_member(CHANNEL_ID, user_id)
            in_channel = channel_member.status in ["member", "administrator", "creator"]
        except:
            in_channel = False
        
        return in_group, in_channel
    except Exception as e:
        logger.error(f"❌ Membership check error: {e}")
        return False, False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start"""
    try:
        user = update.effective_user
        
        # Buat user di database
        db.create_user(user.id, user.username or "", user.first_name or "")
        
        welcome_text = f"""
🎮 **Lucky Wheel Bot - SOLVED VERSION**

👋 Halo {user.first_name}!

🎯 Bot ini sudah diperbaiki untuk memastikan hadiah masuk ke bag dengan benar!

🔗 Join group dan channel dulu:
• Group: https://t.me/+YOURGROUP
• Channel: https://t.me/+YOURCHANNEL

Kirim /menu untuk mulai bermain.
        """
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"✅ User {user.id} started bot")
        
    except Exception as e:
        logger.error(f"❌ /start error: {e}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /menu"""
    try:
        user = update.effective_user
        
        # Buat/cek user di database
        db.create_user(user.id, user.username or "", user.first_name or "")
        
        # Cek membership
        in_group, in_channel = await check_membership(user.id, context.bot)
        
        if not (in_group and in_channel) and user.id != OWNER_ID:
            await update.message.reply_text("⚠️ Kamu harus join group dan channel dulu sebelum bermain!")
            return
        
        # Update membership status
        db.update_user(user.id, join_group=in_group, join_channel=in_channel, 
                      registered=(in_group and in_channel))
        
        # Ambil inventory
        inventory = db.get_user_inventory(user.id)
        if not inventory:
            await update.message.reply_text("❌ Error mengambil inventory!")
            return
        
        menu_text = f"""
🎮 **GAME MENU**

💰 Fizz Coin: **{inventory['fizz_coin']}**
🎫 Lucky Ticket: **{inventory['lucky_ticket']}**
🧪 HP Potion: **{inventory['hp_potion']}**

🎯 Pilih menu di bawah untuk bermain!
        """
        
        keyboard = [
            [InlineKeyboardButton("🎡 Lucky Wheel", callback_data="lucky_wheel")],
            [InlineKeyboardButton("🎒 Inventory", callback_data="inventory")],
            [InlineKeyboardButton("📊 Riwayat Spin", callback_data="history")]
        ]
        
        await update.message.reply_text(
            menu_text, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info(f"✅ Menu shown to user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ /menu error: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk tombol inline"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "lucky_wheel":
            # Cek apakah user punya ticket
            if not db.deduct_ticket(user_id):
                await query.edit_message_text("❌ Kamu tidak punya Lucky Ticket! /menu untuk cek inventory.")
                return
            
            # Buat tombol untuk membuka web app
            webapp_url = f"{WEB_SERVER_URL}/luckywheel.html"
            
            keyboard = [
                [InlineKeyboardButton(
                    "🎡 BUKA LUCKY WHEEL",
                    web_app=WebAppInfo(url=webapp_url)
                )]
            ]
            
            await query.edit_message_text(
                "🎯 Klik tombol di bawah untuk spin!\n\n💡 Pastikan kamu sudah join group & channel ya!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif query.data == "inventory":
            # Tampilkan inventory
            inventory = db.get_user_inventory(user_id)
            if not inventory:
                await query.edit_message_text("❌ Error mengambil inventory!")
                return
            
            inv_text = f"""
🎒 **INVENTORY**

💰 Fizz Coin: **{inventory['fizz_coin']}**
🎫 Lucky Ticket: **{inventory['lucky_ticket']}**
🧪 HP Potion: **{inventory['hp_potion']}**
            """
            
            keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_menu")]]
            
            await query.edit_message_text(
                inv_text, 
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif query.data == "history":
            # Tampilkan riwayat spin
            history = db.get_spin_history(user_id, 5)
            
            if not history:
                history_text = "📊 **RIWAYAT SPIN**\n\nBelum ada riwayat spin."
            else:
                history_lines = []
                for prize_type, prize_value, created_at in history:
                    emoji = "💰" if prize_type == "fizz_coin" else "🎫" if prize_type == "lucky_ticket" else "🧪"
                    history_lines.append(f"{emoji} {prize_value} {prize_type.replace('_', ' ').title()}")
                
                history_text = f"""
📊 **RIWAYAT SPIN TERBARU**

{chr(10).join(history_lines)}
                """
            
            keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_menu")]]
            
            await query.edit_message_text(
                history_text, 
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif query.data == "back_to_menu":
            # Kembali ke menu utama
            await menu(update, context)
            
    except Exception as e:
        logger.error(f"❌ Button handler error: {e}")

async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🛠️ SOLUSI UTAMA: Handler untuk menerima data dari Mini App
    """
    try:
        # Validasi WebAppData
        if not update.message.web_app_data:
            logger.error("❌ No WebAppData received")
            await update.message.reply_text("❌ Data tidak lengkap!")
            return
        
        # Parse data JSON dari Mini App
        try:
            data = json.loads(update.message.web_app_data.data)
            logger.info(f"📨 Received WebAppData: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
            await update.message.reply_text("❌ Format data salah!")
            return
        
        # Validasi required fields
        required_fields = ["user_id", "prize_type", "prize_value"]
        for field in required_fields:
            if field not in data:
                logger.error(f"❌ Missing field: {field}")
                await update.message.reply_text(f"❌ Data tidak lengkap:缺少 {field}")
                return
        
        # Extract data
        try:
            user_id = int(data["user_id"])
            prize_type = str(data["prize_type"])
            prize_value = int(data["prize_value"])
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Data type error: {e}")
            await update.message.reply_text("❌ Format data salah!")
            return
        
        # Validasi prize_type
        valid_prize_types = ["fizz_coin", "lucky_ticket", "hp_potion"]
        if prize_type not in valid_prize_types:
            logger.error(f"❌ Invalid prize_type: {prize_type}")
            await update.message.reply_text(f"❌ Tipe hadiah tidak valid: {prize_type}")
            return
        
        # Validasi user_id cocok dengan yang mengirim
        if user_id != update.effective_user.id:
            logger.error(f"❌ User ID mismatch: expected {update.effective_user.id}, got {user_id}")
            await update.message.reply_text("❌ User ID tidak sesuai!")
            return
        
        logger.info(f"🎯 Processing prize: User {user_id}, Type {prize_type}, Value {prize_value}")
        
        # Tambah hadiah ke database
        success = db.add_prize(user_id, prize_type, prize_value)
        
        if not success:
            await update.message.reply_text("❌ Gagal menyimpan hadiah ke database!")
            return
        
        # Kirim konfirmasi ke user
        prize_emoji = "💰" if prize_type == "fizz_coin" else "🎫" if prize_type == "lucky_ticket" else "🧪"
        prize_name = prize_type.replace('_', ' ').title()
        
        confirm_text = f"""
🎉 **HADIAH BERHASIL DIMASUKKAN!**

{prize_emoji} Kamu mendapat: **{prize_value} {prize_name}**

✅ Hadiah sudah masuk ke bag kamu!

💡 Ketik /menu untuk cek inventory terbaru
        """
        
        await update.message.reply_text(confirm_text, parse_mode=ParseMode.MARKDOWN)
        
        # Kirim ke grup (opsional)
        try:
            group_text = f"""
🎉 **SPIN RESULT!**

👤 User: `{update.effective_user.first_name}` (ID: {user_id})
🎁 Hadiah: **{prize_value} {prize_name}**
            """
            
            await context.bot.send_message(
                GROUP_CHAT_ID,
                group_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to send to group: {e}")
        
        logger.info(f"✅ Prize successfully added to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ WebAppData handler error: {e}")
        await update.message.reply_text("❌ Error memproses hasil spin!")

def update_web_server_url():
    """Update WEB_SERVER_URL (opsional untuk development)"""
    # Dalam production, URL sudah diset ke GitHub Pages
    logger.info(f"🌐 Web Server URL: {WEB_SERVER_URL}")

def main():
    """Main function"""
    try:
        # Build application
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("menu", menu))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # 🛠️ KRITIS: WebAppData handler untuk menerima hasil spin
        app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data_handler))
        
        # Update URL
        update_web_server_url()
        
        logger.info("🚀 Lucky Wheel Bot STARTED with prize system FIXED!")
        logger.info(f"🌐 Web Server URL: {WEB_SERVER_URL}")
        logger.info("🛠️ Prize system: READY")
        
        # Start polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()
