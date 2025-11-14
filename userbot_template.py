from pyrogram import Client, filters
import json, sys, os

DATA_PATH = "data/userbots.json"

if len(sys.argv) < 2:
    print("❌ Argumen user_id diperlukan.")
    sys.exit(1)

user_id = sys.argv[1]

with open(DATA_PATH, "r") as f:
    data = json.load(f)

if user_id not in data:
    print("❌ Data userbot tidak ditemukan.")
    sys.exit(1)

# Ambil dari userbots.json atau fallback ke VPS env
api_id = int(data[user_id].get("api_id") or os.getenv("API_ID"))
api_hash = data[user_id].get("api_hash") or os.getenv("API_HASH")
session_string = data[user_id]["session_string"]

app = Client(session_string, api_id=api_id, api_hash=api_hash)

@app.on_message(filters.me & filters.command("menu", prefixes="."))
async def menu_private(client, message):
    text = (
        "**🧭 MENU USERBOT PRIBADI**\n"
        "• .ping → Cek status userbot\n"
        "• .info → Info akun\n"
        "• .stop → Matikan userbot"
    )
    await message.reply_text(text)

@app.on_message(filters.me & filters.command("ping", prefixes="."))
async def ping_cmd(client, message):
    await message.reply_text("🏓 Pong!")

@app.on_message(filters.me & filters.command("info", prefixes="."))
async def info_cmd(client, message):
    me = await client.get_me()
    await message.reply_text(f"👤 **Userbot Info**\nNama: {me.first_name}\nID: `{me.id}`")

@app.on_message(filters.me & filters.command("stop", prefixes="."))
async def stop_cmd(client, message):
    await message.reply_text("🛑 Userbot dimatikan.")
    await client.stop()

print(f"🤖 Userbot {user_id} sedang dijalankan...")
app.run()
