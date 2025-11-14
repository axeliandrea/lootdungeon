# modules/menu_register.py
from pyrogram import types
import json
from datetime import datetime
import os
import time

# ===== GANTI INI DENGAN CHAT ID NUMERIC =====
CHANNEL_ID = -1002502508906  # contoh channel loots666
GROUP_ID = -1002917701297    # contoh group dengan username publik

# Database player JSON
PLAYER_DB = "data/players.json"
os.makedirs("data", exist_ok=True)

async def register_handler(client, callback, owner_id):
    user_id = callback.from_user.id
    username = callback.from_user.username or str(user_id)

    print(f"[DEBUG] User klik REGISTER: {username} ({user_id})")

    # ===== CEK KEANGGOTAAN =====
    joined_channel, joined_group = False, False
    try:
        await client.get_chat_member(CHANNEL_ID, user_id)
        joined_channel = True
        print(f"[DEBUG] {username} sudah join Channel")
    except Exception as e:
        print(f"[DEBUG] {username} belum join Channel: {e}")

    try:
        await client.get_chat_member(GROUP_ID, user_id)
        joined_group = True
        print(f"[DEBUG] {username} sudah join Group")
    except Exception as e:
        print(f"[DEBUG] {username} belum join Group: {e}")

    # ===== BELUM JOIN SEMUA =====
    if not joined_channel or not joined_group:
        text = "⚠️ Kamu harus join dulu:\n"
        keyboard_buttons = []

        if not joined_channel:
            text += "• Channel\n"
            keyboard_buttons.append(types.InlineKeyboardButton("Join Channel", url="https://t.me/loots666"))
        if not joined_group:
            text += "• Group\n"
            keyboard_buttons.append(types.InlineKeyboardButton("Join Group", url="https://t.me/+0dipRzHtObowNGZl"))

        text += "\nSetelah join, klik tombol *Cek Kembali*"

        # Tombol Cek Kembali dengan timestamp unik
        keyboard_buttons.append(types.InlineKeyboardButton("Cek Kembali", callback_data=f"menu_register|{time.time()}"))

        keyboard = types.InlineKeyboardMarkup([[btn] for btn in keyboard_buttons])

        try:
            await callback.message.edit(text=text, reply_markup=keyboard)
            print(f"[DEBUG] Tampilkan instruksi join untuk {username}")
        except Exception as e:
            print(f"[ERROR] Gagal edit pesan instruksi join: {e}")

        await callback.answer()
        return

    # ===== SUDAH JOIN SEMUA =====
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"✅ Kamu sudah join CH & GC nya, Selamat kamu sudah menjadi player!! 🎉\n\n"
        f"User ID: {user_id}\n"
        f"Username: @{username}\n"
        f"Tanggal Register: {now}"
    )

    # ===== SIMPAN KE DATABASE =====
    try:
        with open(PLAYER_DB, "r") as f:
            players = json.load(f)
    except:
        players = {}

    if str(user_id) not in players:
        players[str(user_id)] = {
            "username": username,
            "joined_channel": joined_channel,
            "joined_group": joined_group,
            "register_date": now
        }
        with open(PLAYER_DB, "w") as f:
            json.dump(players, f, indent=4)
        print(f"[DEBUG] {username} disimpan ke database player.json")

        # ===== KIRIM INFO KE OWNER =====
        try:
            await client.send_message(owner_id,
                                      f"🎉 Player baru:\nUser: @{username}\nID: {user_id}\nRegister: {now}")
        except Exception as e:
            print(f"[WARN] Gagal kirim notifikasi ke OWNER: {e}")

    # ===== TOMBOL BACK TO MENU =====
    keyboard = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu")]]
    )
    try:
        await callback.message.edit(text=text, reply_markup=keyboard)
        print(f"[DEBUG] Tampilkan menu REGISTER untuk {username}")
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            print(f"[ERROR] Gagal edit pesan menu REGISTER: {e}")

    await callback.answer("✅ Kamu sudah terdaftar sebagai player!", show_alert=True)
