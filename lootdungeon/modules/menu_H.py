# ATA/modules/menu_H.py
from pyrogram import types, filters
import json, os

# === Lokasi database achievement ===
ACHIEVEMENT_DB = "ATA/data/achievement_db.json"


# === Fungsi utilitas database ===
def load_achievement_db():
    if not os.path.exists(ACHIEVEMENT_DB):
        return {}
    with open(ACHIEVEMENT_DB, "r") as f:
        return json.load(f)


def save_achievement_db(data):
    os.makedirs(os.path.dirname(ACHIEVEMENT_DB), exist_ok=True)
    with open(ACHIEVEMENT_DB, "w") as f:
        json.dump(data, f, indent=2)


# === Keyboard utama Achievement ===
def achievement_menu_keyboard():
    return types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("👾 Monster", callback_data="achievement_monster"),
            types.InlineKeyboardButton("🃏 Card", callback_data="achievement_card"),
        ],
        [types.InlineKeyboardButton("⬅ Kembali", callback_data="main_menu")]
    ])


# === Handler utama menu Achievement ===
async def menu_H_handler(client, callback):
    text_msg = """🎖️ ACHIEVEMENT 🎖️

Lihat pencapaianmu di sini!
Pilih salah satu submenu di bawah:"""
    await callback.message.edit_text(
        text=text_msg,
        reply_markup=achievement_menu_keyboard()
    )
    await callback.answer()


# === Handler Achievement Monster ===
async def achievement_monster_handler(client, callback):
    user_id = str(callback.from_user.id)
    db = load_achievement_db()
    data = db.get(user_id, {}).get("monster_kills", {})

    if not data:
        text = "👾 Monster Achievement\n\nBelum ada monster yang dikalahkan."
        buttons = [
            [types.InlineKeyboardButton("👾 Monster", callback_data="achievement_monster"),
             types.InlineKeyboardButton("🃏 Card", callback_data="achievement_card")],
            [types.InlineKeyboardButton("⬅ Kembali", callback_data="menu_H")]
        ]
    else:
        text = "👾 Monster Achievement\nDaftar monster yang dikalahkan:"
        for monster, count in data.items():
            text += f"\n- {monster}: {count} kali"
        buttons = [
            [types.InlineKeyboardButton("🃏 Card", callback_data="achievement_card")],
            [types.InlineKeyboardButton("⬅ Kembali", callback_data="menu_H")]
        ]

    await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(buttons))
    await callback.answer()


# === Handler Achievement Card ===
async def achievement_card_handler(client, callback):
    user_id = str(callback.from_user.id)
    db = load_achievement_db()
    data = db.get(user_id, {}).get("cards_collected", {})

    if not data:
        text = "🃏 Card Achievement\n\nBelum ada kartu yang dimiliki."
        buttons = [
            [types.InlineKeyboardButton("👾 Monster", callback_data="achievement_monster"),
             types.InlineKeyboardButton("🃏 Card", callback_data="achievement_card")],
            [types.InlineKeyboardButton("⬅ Kembali", callback_data="menu_H")]
        ]
    else:
        text = "🃏 Card Achievement\nDaftar kartu yang dimiliki:"
        for card, qty in data.items():
            text += f"\n- {card}: {qty} buah"
        buttons = [
            [types.InlineKeyboardButton("👾 Monster", callback_data="achievement_monster")],
            [types.InlineKeyboardButton("⬅ Kembali", callback_data="menu_H")]
        ]

    await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(buttons))
    await callback.answer()


# === REGISTER CALLBACKS (agar bisa dipanggil dari ata_menu) ===
def register(app):
    app.on_callback_query(filters.regex("menu_H"))(menu_H_handler)
    app.on_callback_query(filters.regex("achievement_monster"))(achievement_monster_handler)
    app.on_callback_query(filters.regex("achievement_card"))(achievement_card_handler)
    print("[DEBUG][menu_H] Modul Achievement siap")
