# __main__.py - REVISED
import os
import sys
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
# Import modules - PENTING: Import sebelum sys.path
from modules import ata_menu, menu_H, menu_B, menu_C, menu_D, cekid
# Import lucky wheel functions
from modules.lucky_wheel_utils import (
lucky_wheel_manager,
spin_lucky_wheel,
buy_lucky_wheel_ticket,
get_user_lucky_wheel_status,
get_lucky_wheel_info
)
# ==========================================================
# LOAD ENV
# ==========================================================
load_dotenv()
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
if not all([API_ID, API_HASH, BOT_TOKEN, OWNER_ID]):
print("⚠️ Pastikan semua variabel .env sudah benar")
exit(1)
# ==========================================================
# INIT BOT
# ==========================================================
app = Client("MainBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
# ==========================================================
# REGISTER HANDLERS MODULAR
# ==========================================================
ata_menu.register_handlers(app, OWNER_ID)
cekid.register_handlers(app)
menu_H.register(app)
# ==========================================================
# LUCKY WHEEL COMMAND HANDLERS
# ==========================================================
# Command: /spin - Spin lucky wheel
@app.on_message(filters.private & filters.command(["spin", "luckywheel"]))
async def spin_lucky_wheel_command(client, message):
user_id = message.from_user.id
# Cek apakah bisa spin
can_spin, message_text = lucky_wheel_manager.can_spin(user_id)
if not can_spin:
await message.reply_text(message_text)
return
# Spin lucky wheel
success, spin_message, prize = spin_lucky_wheel(user_id)
if success and prize:
result_text = f"""
🎰 **LUCKY WHEEL SPINNED!** 🎰
{pin_message}
🏆 **HADIAH ANDA:**
{pizza.emoji if 'pizza' in locals() else '🎉'} **{prize.name}**
✨ {prize.description}
"""
# Tambahkan efek jackpot
if "JACKPOT" in prize.name:
result_text += f"""
🎉🎉🎉 **JACKPOT! JACKPOT! JACKPOT!** 🎉🎉🎉
🎊 Congratulations! Anda mendapatkan jackpot terbesar! 🎊
