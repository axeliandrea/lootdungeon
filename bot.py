#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sqlite3
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from telegram.constants import ParseMode

# ============================
# CONFIG
# ============================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
OWNER_ID = 6395738130
GROUP_CHAT_ID = -1002917701297
CHANNEL_ID = -1002502508906

# URL MINI APP
WEB_SERVER_URL = "https://axeliandrea.github.io/lootdungeon"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================
# DATABASE
# ============================
class DatabaseManager:
    def __init__(self, db="bot_database.db"):
        self.db = db
        self.init()

    def init(self):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # USER TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registered BOOLEAN DEFAULT FALSE,
                join_group BOOLEAN DEFAULT FALSE,
                join_channel BOOLEAN DEFAULT FALSE,
                fizz_coin INTEGER DEFAULT 0,
                lucky_ticket INTEGER DEFAULT 3,
                hp_potion INTEGER DEFAULT 0
            )
        """)

        # SPIN HISTORY
        cur.execute("""
            CREATE TABLE IF NOT EXISTS spin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prize_type TEXT,
                prize_value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def get_user(self, uid):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        u = cur.fetchone()
        conn.close()
        return u

    def create_user(self, uid, uname, fname):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (uid, uname, fname))
        conn.commit()
        conn.close()

    def update(self, uid, **kwargs):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        fields = []
        vals = []
        for k, v in kwargs.items():
            fields.append(f"{k}=?")
            vals.append(v)
        vals.append(uid)
        cur.execute(f"UPDATE users SET {','.join(fields)} WHERE user_id=?", vals)
        conn.commit()
        conn.close()

    def add_prize(self, uid, ptype, value):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        if ptype == "fizz_coin":
            cur.execute("UPDATE users SET fizz_coin = fizz_coin + ? WHERE user_id = ?", (value, uid))
        elif ptype == "lucky_ticket":
            cur.execute("UPDATE users SET lucky_ticket = lucky_ticket + ? WHERE user_id = ?", (value, uid))
        elif ptype == "hp_potion":
            cur.execute("UPDATE users SET hp_potion = hp_potion + ? WHERE user_id = ?", (value, uid))

        cur.execute("INSERT INTO spin_history (user_id, prize_type, prize_value) VALUES (?, ?, ?)",
                    (uid, ptype, value))

        conn.commit()
        conn.close()

    def deduct_ticket(self, uid):
        if uid == OWNER_ID:
            return True
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute("SELECT lucky_ticket FROM users WHERE user_id=?", (uid,))
        t = cur.fetchone()
        if t and t[0] > 0:
            cur.execute("UPDATE users SET lucky_ticket = lucky_ticket - 1 WHERE user_id=?", (uid,))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def inventory(self, uid):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute("SELECT fizz_coin, lucky_ticket, hp_potion FROM users WHERE user_id=?", (uid,))
        r = cur.fetchone()
        conn.close()
        if r:
            return {"fizz_coin": r[0], "lucky_ticket": r[1], "hp_potion": r[2]}
        return None


db = DatabaseManager()


# ============================
# MEMBERSHIP CHECK
# ============================
async def check_membership(uid, bot):
    try:
        g = await bot.get_chat_member(GROUP_CHAT_ID, uid)
        c = await bot.get_chat_member(CHANNEL_ID, uid)
        return (
            g.status in ["member", "administrator", "creator"],
            c.status in ["member", "administrator", "creator"]
        )
    except:
        return False, False


# ============================
# COMMAND: START
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.create_user(u.id, u.username, u.first_name)

    msg = f"""
🎮 **Lucky Wheel Bot aktif!**

👋 Halo {u.first_name}!

Join dulu sebelum bermain:
🔗 Group: https://t.me/+YOURGROUP
🔗 Channel: https://t.me/+YOURCHANNEL

Kirim /menu untuk mulai bermain.
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


# ============================
# COMMAND: MENU
# ============================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.create_user(u.id, u.username, u.first_name)

    ing, inch = await check_membership(u.id, context.bot)

    db.update(u.id, join_group=ing, join_channel=inch, registered=ing and inch)

    if not (ing and inch) and u.id != OWNER_ID:
        await update.message.reply_text("⚠️ Kamu harus join group + channel dulu.")
        return

    inv = db.inventory(u.id)
    text = f"""
🎮 **GAME MENU**

💰 Fizz Coin: {inv['fizz_coin']}
🎫 Lucky Ticket: {inv['lucky_ticket']}
🧪 HP Potion: {inv['hp_potion']}
"""

    kb = [
        [InlineKeyboardButton("🎡 Lucky Wheel", callback_data="lucky")],
        [InlineKeyboardButton("🎒 Inventory", callback_data="inv")]
    ]
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=InlineKeyboardMarkup(kb))


# ============================
# CALLBACK BUTTONS
# ============================
async def button_handler(update: Update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    if q.data == "lucky":
        # Check ticket
        if not db.deduct_ticket(uid):
            await q.edit_message_text("❌ Kamu tidak punya Lucky Ticket!")
            return

        url = f"{WEB_SERVER_URL}/luckywheel.html"

        kb = [
            [InlineKeyboardButton(
                "🎡 BUKA LUCKY WHEEL",
                web_app=WebAppInfo(url=url)
            )]
        ]
        await q.edit_message_text(
            "Klik tombol di bawah untuk spin!",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif q.data == "inv":
        inv = db.inventory(uid)
        msg = f"""
🎒 **INVENTORY**

💰 Fizz Coin: {inv['fizz_coin']}
🎫 Lucky Ticket: {inv['lucky_ticket']}
🧪 HP Potion: {inv['hp_potion']}
"""
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)


# ============================
# RECEIVER HASIL SPIN MINI APP
# ============================
async def lucky_wheel_receiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menerima WebAppData dari Mini App."""
    try:
        data = json.loads(update.message.web_app_data.data)

        uid = int(data["user_id"])
        ptype = data["prize_type"]
        pvalue = int(data["prize_value"])

        # Simpan hadiah ke database
        db.add_prize(uid, ptype, pvalue)

        # Kirim konfirmasi ke user
        await update.message.reply_text(
            f"🎉 Kamu mendapat **{pvalue} {ptype.replace('_', ' ').title()}**!"
        )

        # KIRIM ANNOUNCEMENT KE GROUP
        await context.bot.send_message(
            GROUP_CHAT_ID,
            f"""
🎉 **SPIN RESULT!**

👤 Player ID: `{uid}`
🎁 Hadiah: **{pvalue} {ptype.replace('_', ' ').title()}**
""",
            parse_mode=ParseMode.MARKDOWN
        )

        logger.info(f"[SPIN] UID {uid} mendapat {pvalue} {ptype}")

    except Exception as e:
        logger.error(f"Spin receiver error: {e}")
        await update.message.reply_text("❌ Gagal memproses hasil spin.")


# ============================
# MAIN
# ============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    # WebAppData Handler
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, lucky_wheel_receiver))

    logger.info("BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
