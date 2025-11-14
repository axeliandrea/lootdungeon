# modules/cekid.py
import re
from pyrogram import Client, filters

def register_handlers(app: Client):
    print("[DEBUG][cekid] Modul cekid siap")

    @app.on_message(filters.command("getid") & (filters.private | filters.group | filters.channel))
    async def get_id(client, message):
        chat_type = message.chat.type
        user_id = message.from_user.id if message.from_user else "Unknown"
        chat_id = message.chat.id

        text = (
            f"📌 Info ID:\n"
            f"• User ID: {user_id}\n"
            f"• Chat ID: {chat_id}\n"
        )

        # DETEKSI LINK PRIVATE t.me/c/<id>
        links_private = re.findall(r"(?:https?://)?t\.me/c/(\d+)", message.text or "")
        for link_id in links_private:
            try:
                channel_id = int(f"-100{link_id}")
                text += f"\n• Private Channel/Supergroup ID: {channel_id}"
            except ValueError:
                text += f"\n⚠️ Tidak bisa convert ID dari link t.me/c/{link_id}"

        # DETEKSI LINK PUBLIK t.me/<username> atau t.me/<username>/<message_id>
        links_public = re.findall(r"(?:https?://)?t\.me/([\w\d_]+)(?:/\d+)?", message.text or "")
        for username in links_public:
            try:
                chat = await client.get_chat(username)
                chat_type_str = str(chat.type).split('.')[-1].capitalize()
                text += f"\n• Public {chat_type_str} @{username} → ID: {chat.id}"
            except Exception as e:
                text += f"\n⚠️ Gagal mendapatkan info @{username} (Error: {e})"


        await message.reply_text(text)
