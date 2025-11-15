#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sqlite3
import json
import hashlib
from datetime import datetime
from urllib.parse import urljoin

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Konfigurasi Bot
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
OWNER_ID = 6395738130
GROUP_CHAT_ID = -1002917701297
CHANNEL_ID = -1002502508906

# URL untuk Mini App (akan diupdate setelah web server running)
WEB_SERVER_URL = "https://lootdungeon.online/luckywheel.html"  # Akan diupdate otomatis

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database Manager
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
        
        # Insert default prizes
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
    
    def get_user(self, user_id):
        """Ambil data user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_user(self, user_id, username, first_name):
        """Buat data user baru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()
    
    def update_user_status(self, user_id, **kwargs):
        """Update status user"""
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
    
    def get_prizes(self):
        """Ambil semua hadiah dengan probabilitas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prizes')
        prizes = cursor.fetchall()
        conn.close()
        return prizes
    
    def add_prize_to_user(self, user_id, prize_type, prize_value):
        """Tambah hadiah ke inventory user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update inventory user
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
        
        # Tambah ke history
        cursor.execute('''
            INSERT INTO spin_history (user_id, prize_type, prize_value)
            VALUES (?, ?, ?)
        ''', (user_id, prize_type, prize_value))
        
        conn.commit()
        conn.close()
    
    def deduct_ticket(self, user_id):
        """Kurangi 1 tiket dari user (kecuali owner)"""
        if user_id == OWNER_ID:
            return True
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cek apakah user punya tiket
        cursor.execute('SELECT lucky_ticket FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            cursor.execute('''
                UPDATE users SET lucky_ticket = lucky_ticket - 1
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_user_inventory(self, user_id):
        """Ambil inventory user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fizz_coin, lucky_ticket, hp_potion
            FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'fizz_coin': result[0],
                'lucky_ticket': result[1],
                'hp_potion': result[2]
            }
        return None

# Fungsi untuk memeriksa membership
async def check_user_membership(user_id, bot):
    """Periksa apakah user sudah join group dan channel"""
    try:
        # Cek group membership
        group_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
        in_group = group_member.status in ['member', 'administrator', 'creator']
        
        # Cek channel membership
        channel_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        in_channel = channel_member.status in ['member', 'administrator', 'creator']
        
        return in_group, in_channel
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False, False

# Inisialisasi database
db = DatabaseManager()

# Handler untuk command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    user = update.effective_user
    
    # Buat atau update data user
    db.create_user(user.id, user.username, user.first_name)
    
    # Periksa membership
    in_group, in_channel = await check_user_membership(user.id, context.bot)
    
    if user.id == OWNER_ID:
        db.update_user_status(user.id, registered=True, join_group=True, join_channel=True)
    
    message = f"""
🎮 **Lucky Wheel Bot sudah aktif!**

👋 Halo {user.first_name}!

Untuk mulai bermain, kamu harus:
1️⃣ Join Group Chat: https://t.me/{GROUP_CHAT_ID}
2️⃣ Join Channel: https://t.me/{CHANNEL_ID}

Ketik /menu untuk melihat semua fitur yang tersedia.

**Reward yang bisa didapat:**
💰 Fizz Coin untuk belanja
🎫 Lucky Ticket untuk spin roulette
🧪 HP Potion untuk healing
☠️ Zonk (手氣不順)

Selamat bermain! 🍀
"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# Handler untuk command /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /menu"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if not user_data:
        db.create_user(user.id, user.username, user.first_name)
        user_data = db.get_user(user.id)
    
    in_group, in_channel = await check_user_membership(user.id, context.bot)
    
    # Update membership status di database
    if user.id != OWNER_ID:
        db.update_user_status(
            user.id,
            join_group=in_group,
            join_channel=in_channel,
            registered=in_group and in_channel
        )
    
    if not in_group or not in_channel:
        message = """
⚠️ **Syarat belum terpenuhi!**

Untuk mengakses semua fitur, kamu harus:
1️⃣ Join Group Chat: https://t.me/{GROUP_CHAT_ID}
2️⃣ Join Channel: https://t.me/{CHANNEL_ID}

Setelah join, ketik /menu lagi untuk melihat menu game.
"""
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        return
    
    # Buat keyboard menu 3x3
    keyboard = [
        [InlineKeyboardButton("📝 REGISTER", callback_data="register"),
         InlineKeyboardButton("🎡 LUCKY WHEEL", callback_data="lucky_wheel"),
         InlineKeyboardButton("🎒 INVENTORY", callback_data="inventory")],
        
        [InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon"),
         InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon"),
         InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon")],
        
        [InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon"),
         InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon"),
         InlineKeyboardButton("⏳ COMING SOON", callback_data="coming_soon")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Ambil data inventory
    inventory = db.get_user_inventory(user.id)
    if inventory:
        inventory_text = f"""
📊 **Status Player:**
💰 Fizz Coin: {inventory['fizz_coin']:,}
🎫 Lucky Ticket: {inventory['lucky_ticket']:,}
🧪 HP Potion: {inventory['hp_potion']:,}
"""
    else:
        inventory_text = ""
    
    message = f"""
🎮 **Lucky Wheel Game Menu**

{inventory_text}

Pilih menu di bawah untuk bermain:
"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# Handler untuk callback query
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback button"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    
    if query.data == "register":
        in_group, in_channel = await check_user_membership(user_id, context.bot)
        
        if user_id == OWNER_ID:
            message = "✅ **OWNER STATUS**\nKamu adalah owner bot ini dan memiliki akses unlimited!"
        elif in_group and in_channel:
            db.update_user_status(user_id, registered=True)
            message = """
✅ **REGISTRASI BERHASIL!**

Selamat! Kamu sudah terdaftar sebagai player aktif.

✨ **Keuntungan:**
- Tiket Lucky Wheel gratis untuk memulai
- Akses ke semua fitur game
- Dapat hadia-hadiah menarik dari roulette

Ketik /menu untuk mulai bermain!
"""
        else:
            status = []
            if not in_group:
                status.append("❌ Group Chat")
            else:
                status.append("✅ Group Chat")
            
            if not in_channel:
                status.append("❌ Channel")
            else:
                status.append("✅ Channel")
            
            message = f"""
📝 **Status Registrasi**

{' / '.join(status)}

Untuk melengkapi registrasi:
1️⃣ Join Group Chat: https://t.me/{GROUP_CHAT_ID}
2️⃣ Join Channel: https://t.me/{CHANNEL_ID}

Setelah join semua, klik tombol ini lagi.
"""
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    elif query.data == "lucky_wheel":
        # Cek ticket dan membership
        user_data = db.get_user(user_id)
        if not user_data:
            await query.edit_message_text("❌ Data tidak ditemukan. Ketik /start dulu.")
            return
        
        in_group, in_channel = await check_user_membership(user_id, context.bot)
        
        if user_id != OWNER_ID and (not user_data[3] or not in_group or not in_channel):
            await query.edit_message_text("❌ Selesaikan registrasi dulu di menu REGISTER!")
            return
        
        # Cek tiket
        if user_id != OWNER_ID:
            has_ticket = db.deduct_ticket(user_id)
            if not has_ticket:
                await query.edit_message_text("❌ Kamu tidak memiliki Lucky Ticket!\n\nBelanja di shop atau ikuti event untuk mendapatkannya.")
                return
        
        # Buka Mini App untuk Lucky Wheel
        web_app_data = {
            "user_id": user_id,
            "username": user.username or user.first_name,
            "is_owner": user_id == OWNER_ID
        }
        
        # Buat URL Mini App
        webapp_url = f"{WEB_SERVER_URL}/luckywheel.html"
        
        keyboard = [
            [InlineKeyboardButton(
                "🎡 BUKA LUCKY WHEEL",
                url=webapp_url,
                web_app={"url": webapp_url, "data": web_app_data}
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
🎡 **Lucky Wheel Roulette**

{'(🏆 OWNER MODE - Tiket Unlimited)' if user_id == OWNER_ID else ''}

🔄 **Hadiah yang tersedia:**
💰 1x = 100 Fizz Coin
💰 3x = 300 Fizz Coin  
💰 5x = 500 Fizz Coin
🎫 1x = 1 Lucky Ticket
🎫 3x = 3 Lucky Ticket
🎫 5x = 5 Lucky Ticket
🧪 5x = 5 HP Potion
☠️ = Zonk

{'✅ Tiket sudah dikurangi' if user_id != OWNER_ID else '✅ Owner Mode Active'}

Klik tombol di bawah untuk membuka Lucky Wheel!
"""
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    elif query.data == "inventory":
        # Ambil data inventory
        inventory = db.get_user_inventory(user_id)
        if not inventory:
            await query.edit_message_text("❌ Inventory tidak ditemukan.")
            return
        
        keyboard = [
            [InlineKeyboardButton("🎒 LIHAT SEMUA ITEM", callback_data="view_inventory"),
             InlineKeyboardButton("🧪 GUNAKAN HP POTION", callback_data="use_hp_potion")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
🎒 **Inventory Menu**

📊 **Ringkasan Inventory:**
💰 Fizz Coin: {inventory['fizz_coin']:,}
🎫 Lucky Ticket: {inventory['lucky_ticket']:,}
🧪 HP Potion: {inventory['hp_potion']:,}

{'(🏆 OWNER MODE - Tiket Unlimited)' if user_id == OWNER_ID else ''}
"""
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    elif query.data == "view_inventory":
        # Tampilkan semua item detail
        inventory = db.get_user_inventory(user_id)
        if not inventory:
            await query.edit_message_text("❌ Inventory kosong.")
            return
        
        message = f"""
🎒 **Detail Inventory**

💰 **Fizz Coin:** {inventory['fizz_coin']:,}
   → Bisa digunakan untuk belanja di shop

🎫 **Lucky Ticket:** {inventory['lucky_ticket']:,}
   → Untuk spin Lucky Wheel Roulette

🧪 **HP Potion:** {inventory['hp_potion']:,}
   → Untuk menambah HP karakter

{'(🏆 OWNER MODE - Tiket Unlimited)' if user_id == OWNER_ID else ''}

 Semua hadiah yang didapat dari Lucky Wheel akan tersimpan di sini!
"""
        
        await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    
    elif query.data == "use_hp_potion":
        inventory = db.get_user_inventory(user_id)
        if not inventory or inventory['hp_potion'] <= 0:
            await query.edit_message_text("❌ Kamu tidak memiliki HP Potion!")
            return
        
        # Kurangi 1 HP potion dan berikan effect (untuk saat ini just info)
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET hp_potion = hp_potion - 1
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
        
        await query.edit_message_text("🧪 **HP Potion digunakan!**\n\nHP kamu sudah bertambah!\n(Untuk implementasi game RPG, fitur ini akan dikembangkan lebih lanjut)")
    
    elif query.data == "coming_soon":
        await query.edit_message_text("⏳ **Fitur ini sedang dalam pengembangan!**\n\nNantikan update terbaru!")
    
    elif query.data == "spin_result":
        # Handle hasil spin dari Mini App
        try:
            # Parse data dari callback
            data = json.loads(query.data.replace("spin_result:", ""))
            prize_type = data.get('prize_type')
            prize_value = data.get('prize_value')
            
            # Tambah hadiah ke inventory
            db.add_prize_to_user(user_id, prize_type, prize_value)
            
            # Ambil emoji dan nama hadiah
            prizes = db.get_prizes()
            prize_emoji = "❓"
            prize_name = "Unknown"
            
            for prize in prizes:
                if prize[1] == prize_value and prize[2].lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '') == prize_type.replace('_', '_'):
                    prize_emoji = prize[4]
                    prize_name = prize[3]
                    break
            
            if prize_type == "zonk":
                message = f"""
☠️ **HASIL SPIN: ZONK!**

Sayang sekali, kamu tidak mendapat hadiah kali ini.

Tapi jangan menyerah! Coba lagi untuk mendapatkan hadiah menarik!

Ketik /menu untuk bermain lagi.
"""
            else:
                # Konversi nama hadiah
                type_names = {
                    'fizz_coin': 'Fizz Coin',
                    'lucky_ticket': 'Lucky Ticket',
                    'hp_potion': 'HP Potion'
                }
                type_name = type_names.get(prize_type, prize_type)
                
                message = f"""
🎉 **SELAMAT! KAMU MENDAPAT:**

{prize_emoji} **{prize_value} {type_name}**

Hadiah sudah masuk ke inventory kamu!

Ketik /menu untuk bermain lagi atau cek inventory untuk melihat koleksi kamu.
"""
            
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error processing spin result: {e}")
            await query.edit_message_text("❌ Terjadi kesalahan saat memproses hasil spin.")

# API untuk Mini App
async def handle_lucky_wheel_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hasil spin dari Mini App"""
    try:
        data = json.loads(update.message.text)
        user_id = data.get('user_id')
        prize_type = data.get('prize_type')
        prize_value = data.get('prize_value')
        
        # Tambah hadiah ke inventory
        db.add_prize_to_user(user_id, prize_type, prize_value)
        
        # Kirim konfirmasi
        await update.message.reply_text("✅ Hasil spin berhasil disimpan!")
        
    except Exception as e:
        logger.error(f"Error handling lucky wheel result: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat menyimpan hasil spin.")

# Fungsi untuk update Web Server URL
def update_web_server_url():
    """Update URL web server untuk Mini App"""
    global WEB_SERVER_URL
    try:
        import requests
        import socket
        
        # Dapatkan IP lokal
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        WEB_SERVER_URL = f"http://{local_ip}:8081"
        logger.info(f"Web Server URL updated to: {WEB_SERVER_URL}")
        
    except Exception as e:
        logger.error(f"Error updating web server URL: {e}")

# Main function
def main():
    """Fungsi utama untuk menjalankan bot"""
    # Update web server URL
    update_web_server_url()
    
    # Buat application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Tambahkan handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
