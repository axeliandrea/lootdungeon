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
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
OWNER_ID = 6395738130
GROUP_CHAT_ID = -1002917701297
CHANNEL_ID = -1002502508906
WEB_SERVER_URL = "https://axeliandrea.github.io/lootdungeon"

# Logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs
logger = logging.getLogger(__name__)

# ============================
# DATABASE
# ============================
class DatabaseManager:
    def __init__(self, db="bot_database.db"):
        self.db = db
        self.init()

    def init(self):
        logger.debug("Initializing database...")
        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            # Create table for users
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
            # Create table for spin history
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
            logger.debug("Database initialized successfully.")
        except Exception as e:
            logger.error(f"DB init error: {e}")
        finally:
            conn.close()

    def get_user(self, uid):
        logger.debug(f"Fetching user {uid}")
        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
            u = cur.fetchone()
            logger.debug(f"User fetched: {u}")
            return u
        except Exception as e:
            logger.error(f"DB get_user error: {e}")
        finally:
            conn.close()

    def create_user(self, uid, uname, fname):
        logger.debug(f"Creating user {uid}, uname={uname}, fname={fname}")
        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (uid, uname, fname))
            conn.commit()
            logger.debug("User creation committed.")
        except Exception as e:
            logger.error(f"DB create_user error: {e}")
        finally:
            conn.close()

    def update(self, uid, **kwargs):
        logger.debug(f"Updating user {uid} with {kwargs}")
        try:
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
            logger.debug("User update committed.")
        except Exception as e:
            logger.error(f"DB update error: {e}")
        finally:
            conn.close()

    def add_prize(self, uid, ptype, value):
        logger.debug(f"Adding prize: uid={uid}, type={ptype}, value={value}")
        try:
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
            logger.debug("Prize added and committed.")
        except Exception as e:
            logger.error(f"DB add_prize error: {e}")
        finally:
            conn.close()

    def deduct_ticket(self, uid):
        logger.debug(f"Deducting ticket for user {uid}")
        try:
            if uid == OWNER_ID:
                logger.debug("Owner detected, skipping deduction.")
                return True
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute("SELECT lucky_ticket FROM users WHERE user_id=?", (uid,))
            t = cur.fetchone()
            if t and t[0] > 0:
                cur.execute("UPDATE users SET lucky_ticket = lucky_ticket - 1 WHERE user_id=?", (uid,))
                conn.commit()
                logger.debug("Ticket deducted.")
                return True
            logger.debug("No ticket to deduct.")
            return False
        except Exception as e:
            logger.error(f"DB deduct_ticket error: {e}")
            return False
        finally:
            conn.close()

    def inventory(self, uid):
        logger.debug(f"Fetching inventory for user {uid}")
        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute("SELECT fizz_coin, lucky_ticket, hp_potion FROM users WHERE user_id=?", (uid,))
            r = cur.fetchone()
            logger.debug(f"Inventory: {r}")
            if r:
                return {"fizz_coin": r[0], "lucky_ticket": r[1], "hp_potion": r[2]}
            return None
        except Exception as e:
            logger.error(f"DB inventory error: {e}")
            return None
        finally:
            conn.close()


db = DatabaseManager()


# ============================
# MEMBERSHIP CHECK
# ============================
async def check_membership(uid, bot):
    logger.debug(f"Checking membership for user {uid}")
    try:
        g = await bot.get_chat_member(GROUP_CHAT_ID, uid)
        c = await bot.get_chat_member(CHANNEL_ID, uid)
        g_status = g.status in ["member", "administrator", "creator"]
        c_status = c.status in ["member", "administrator", "creator"]
        logger.debug(f"Group: {g_status}, Channel: {c_status}")
        return g_status, c_status
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False, False


# ============================
# COMMANDS
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"/start triggered by {update.effective_user.id}")
    try:
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
    except Exception as e:
        logger.error(f"/start error: {e}")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"/menu triggered by {update.effective_user.id}")
    try:
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
    except Exception as e:
        logger.error(f"/menu error: {e}")


async def button_handler(update: Update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    if q.data == "lucky":
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
        logger.debug(f"Received WebAppData: {data}")

        uid = int(data["user_id"])
        ptype = data["prize_type"]
        pvalue = int(data["prize_value"])

        # Simpan hadiah ke database
        db.add_prize(uid, ptype, pvalue)

        # Kirim konfirmasi ke user
        await update.message.reply_text(
            f"🎉 Kamu mendapat **{pvalue} {ptype.replace('_', ' ').title()}**!"
        )

        # Kirim pengumuman ke grup
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
