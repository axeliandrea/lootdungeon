# __main__.py
import os
import sys
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from modules import ata_menu, menu_H, menu_B, menu_C, menu_D, cekid

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
# COMMAND /restart (OWNER only)
# ==========================================================
@app.on_message(filters.private & filters.command("restart") & filters.user(OWNER_ID))
async def restart_bot(client, message):
    await message.reply_text("♻️ Bot sedang restart...")
    print("🔄 Restart bot oleh OWNER")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ==========================================================
# COMMAND /help
# ==========================================================
@app.on_message(filters.private & filters.command("help"))
async def help_command(client, message):
    help_text = (
        "❓ *HELP MENU*\n\n"
        "• /restart → Restart bot (hanya OWNER)\n"
        "• /help → Tampilkan informasi ini\n"
        "• /getid → Cek User ID, Chat ID, atau Channel ID\n"
        "• /activate → Tampilkan menu tombol REGISTER / MENU B–I"
    )
    await message.reply_text(help_text)

# ==========================================================
# DEBUG PRIVATE MESSAGE
# ==========================================================
@app.on_message(filters.private, group=99)
async def debug_message(client, message):
    if message.text and message.text.startswith("/"):
        return
    user_id = message.from_user.id if message.from_user else "Unknown"
    username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else str(user_id)
    print(f"[DEBUG] Pesan dari {username}: {message.text}")

# ==========================================================
# RUN BOT
# ==========================================================
if __name__ == "__main__":
    print("🚀 Bot utama aktif!")

    app.run()


