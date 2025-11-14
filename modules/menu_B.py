# ATA/ATA/modules/menu_B.py 05:33
from pyrogram import types, filters
import json, os, time, asyncio
import math

DB_FILE = "data/hero_data.json"   # database hero
PLAYER_DB = "data/players.json"  # database player
CREATION_STATE = {}
ACTIVE_SLOT = {}
MAX_LEVEL = 50

CLASS_STATS = {
    "Swordman": {"STR": 1, "AGI": 1, "VIT": 1, "INT": 1, "DEX": 1, "LUK": 1},
    "Mage": {"STR": 1, "AGI": 1, "VIT": 1, "INT": 1, "DEX": 1, "LUK": 1},
    "Thief": {"STR": 1, "AGI": 1, "VIT": 1, "INT": 1, "DEX": 1, "LUK": 1},
    "Acolyte": {"STR": 1, "AGI": 1, "VIT": 1, "INT": 1, "DEX": 1, "LUK": 1}
}

# ============================
# EXP Table
# ============================
EXP_TABLE = []
BASE_EXP = 100
for lvl in range(1, MAX_LEVEL):
    if lvl == 1:
        EXP_TABLE.append(BASE_EXP)
    else:
        exp_needed = int(BASE_EXP * ((lvl+1)**2.5) * 3)
        EXP_TABLE.append(exp_needed)

# ============================
# Level up stats per class
# ============================
LEVEL_UP_STATS = {
    "Swordman": {"STR":3, "AGI":1, "VIT":2, "INT":0, "DEX":1, "LUK":0},
    "Mage":    {"STR":0, "AGI":1, "VIT":1, "INT":3, "DEX":1, "LUK":0},
    "Thief":   {"STR":1, "AGI":3, "VIT":1, "INT":0, "DEX":2, "LUK":1},
    "Acolyte": {"STR":1, "AGI":0, "VIT":1, "INT":2, "DEX":0, "LUK":1},
}

# ============================
# Utility: Load / Save
# ============================
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_hero_db():
    db = load_json(DB_FILE)
    if not isinstance(db, dict):
        db = {}
    for user_id, heroes in db.items():
        if not isinstance(heroes, dict):
            db[user_id] = {}
            heroes = db[user_id]
        for slot, hero in list(heroes.items()):
            if not isinstance(hero, dict):
                heroes[slot] = {}
                hero = heroes[slot]
            hero.setdefault("name", f"Hero-{slot}")
            hero.setdefault("class", "Swordman")
            hero.setdefault("gender", "Male")
            hero.setdefault("level", 1)
            hero.setdefault("exp", 0)
            hero.setdefault("hp", 100)
            hero.setdefault("mp", 50)
            hero.setdefault("base_stats", CLASS_STATS.get(hero["class"], CLASS_STATS["Swordman"]).copy())
            hero.setdefault("equipment", {})
    return db

def save_hero_db(db):
    save_json(DB_FILE, db)

# ============================
# Hero level up
# ============================
def check_level_up(hero):
    leveled_up = False
    while hero["level"] < MAX_LEVEL:
        current_level = hero["level"]
        exp_needed = EXP_TABLE[current_level-1]
        if hero["exp"] >= exp_needed:
            hero["level"] += 1
            class_name = hero["class"]
            stats_up = LEVEL_UP_STATS.get(class_name, {})
            for stat, inc in stats_up.items():
                hero["base_stats"][stat] += inc
            leveled_up = True
        else:
            break
    return leveled_up

# ============================
# Hero regeneration task
# ============================
from modules.menu_B import load_hero_db, save_hero_db
import asyncio

USER_REGEN_MSG = {}   # user_id: message_id
USER_REGEN_TEXT = {}  # user_id: last_text

async def hero_regeneration_task(app):
    while True:
        await asyncio.sleep(5)
        hero_db = load_hero_db()

        for user_id, user_heroes in hero_db.items():
            notif_lines = []
            any_regen = False
            for slot, hero in user_heroes.items():
                if hero.get("hp",0) <= 0:
                    continue

                regen_hp = 0
                regen_mp = 0

                if hero["hp"] < 100:
                    regen_hp = min(5, 100 - hero["hp"])
                    hero["hp"] += regen_hp
                    any_regen = True

                if hero["mp"] < 50:
                    regen_mp = min(2, 50 - hero["mp"])
                    hero["mp"] += regen_mp
                    any_regen = True

                line = f"💚 Hero Slot {slot}: HP {hero['hp']}/100 MP {hero['mp']}/50"
                notif_lines.append(line)

            save_hero_db(hero_db)
            text = "⏱️ Regen Hero:\n" + "\n".join(notif_lines)

            try:
                # cek dulu apakah teks berubah
                if user_id in USER_REGEN_MSG:
                    if USER_REGEN_TEXT.get(user_id) != text:
                        await app.edit_message_text(int(user_id), USER_REGEN_MSG[user_id], text)
                        USER_REGEN_TEXT[user_id] = text
                else:
                    msg = await app.send_message(int(user_id), text)
                    USER_REGEN_MSG[user_id] = msg.id
                    USER_REGEN_TEXT[user_id] = text
            except Exception as e:
                print(f"[DEBUG] Gagal kirim/edit regen ke {user_id}: {e}")


# ============================
# Keyboards
# ============================
def hero_slot_keyboard(user_heroes):
    keyboard = []
    for i in range(1, 4):
        slot_str = str(i)
        h = user_heroes.get(slot_str)
        if isinstance(h, dict) and "name" in h and "class" in h:
            keyboard.append([types.InlineKeyboardButton(
                f"Slot {i} ✅ {h['name']} ({h['class']}) Lv {h.get('level',1)}",
                callback_data=f"hero_slot_{i}"
            )])
        else:
            keyboard.append([types.InlineKeyboardButton(
                f"Slot {i} 🔓 (Empty)",
                callback_data=f"hero_slot_{i}"
            )])
    keyboard.append([types.InlineKeyboardButton("⬅ Back", callback_data="main_menu")])
    return types.InlineKeyboardMarkup(keyboard)

def gender_keyboard():
    keyboard = [
        [types.InlineKeyboardButton("Male ♂️", callback_data="gender_Male"),
         types.InlineKeyboardButton("Female ♀️", callback_data="gender_Female")],
        [types.InlineKeyboardButton("⬅ Back", callback_data="menu_B")]
    ]
    return types.InlineKeyboardMarkup(keyboard)

def class_keyboard():
    keyboard = [
        [types.InlineKeyboardButton("Swordman ⚔️", callback_data="create_hero_Swordman"),
         types.InlineKeyboardButton("Mage 🪄", callback_data="create_hero_Mage")],
        [types.InlineKeyboardButton("Thief 🗡️", callback_data="create_hero_Thief"),
         types.InlineKeyboardButton("Acolyte ✝️", callback_data="create_hero_Acolyte")],
        [types.InlineKeyboardButton("⬅ Back", callback_data="menu_B")]
    ]
    return types.InlineKeyboardMarkup(keyboard)

# ============================
# Register callbacks
# ============================
def register(app, owner_id):
    # Start regeneration loop
    app.loop.create_task(hero_regeneration_task(app))

    @app.on_callback_query(filters.regex("menu_B"))
    async def menu_B_handler(client, callback):
        user_id = str(callback.from_user.id)
        player_db = load_json(PLAYER_DB)
        if user_id not in player_db:
            warning_msg = "```text\n⚠️ KAMU BELUM REGISTER ⚠️\n\nKamu belum terdaftar sebagai player.\nSilakan register terlebih dahulu di menu utama.\n```"
            await callback.message.edit_text(
                warning_msg,
                reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("⬅ Kembali ke Menu Utama", callback_data="main_menu")]])
            )
            await callback.answer()
            return
        db = load_hero_db()
        user_heroes = db.get(user_id, {})
        msg = "```text\n🛡️ MY HERO MENU 🛡️\n\nPilih slot hero yang ingin kamu lihat atau buat:\n```"
        await callback.message.edit_text(msg, reply_markup=hero_slot_keyboard(user_heroes))
        await callback.answer()

    @app.on_callback_query(filters.regex(r"hero_slot_"))
    async def hero_slot_cb(client, callback):
        user_id = str(callback.from_user.id)
        slot = callback.data.replace("hero_slot_", "")
        ACTIVE_SLOT[user_id] = slot
        db = load_hero_db()
        user_heroes = db.get(user_id, {})
        h = user_heroes.get(slot)
        if isinstance(h, dict) and "name" in h and "class" in h:
            stats = "\n".join([f"{k:<5}: {v}" for k, v in h.get("base_stats", {}).items()])
            hero_info = f"""```text
🛡️ Hero Slot {slot} 🛡️
Name   : {h['name']}
Class  : {h['class']}
Gender : {h['gender']}
Level  : {h.get('level',1)}
Exp    : {h.get('exp',0)}
HP     : {h.get('hp',0)} 💖
MP     : {h.get('mp',0)} 🔋

Stats:
{stats}
```"""
            keyboard = types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("Delete Hero ❌", callback_data=f"delete_hero_{slot}")],
                [types.InlineKeyboardButton("⬅ Back", callback_data="menu_B")]
            ])
            await callback.message.edit_text(hero_info, reply_markup=keyboard)
        else:
            msg = f"```text\n🛡️ CREATE HERO 🛡️\n\nSlot {slot} masih kosong.\nPilih class untuk hero baru:\n```"
            await callback.message.edit_text(msg, reply_markup=class_keyboard())
        await callback.answer()

    # Hero creation callbacks
    @app.on_callback_query(filters.regex(r"create_hero_"))
    async def create_hero_cb(client, callback):
        user_id = str(callback.from_user.id)
        hero_class = callback.data.replace("create_hero_", "")
        CREATION_STATE[user_id] = {"slot": ACTIVE_SLOT.get(user_id), "class": hero_class}
        msg = f"```text\n🛡️ CREATE HERO 🛡️\n\nClass : {hero_class}\nSilakan pilih gender:\n```"
        await callback.message.edit_text(msg, reply_markup=gender_keyboard())
        await callback.answer()

    @app.on_callback_query(filters.regex(r"gender_"))
    async def gender_cb(client, callback):
        user_id = str(callback.from_user.id)
        if user_id not in CREATION_STATE:
            return
        gender = callback.data.replace("gender_", "")
        CREATION_STATE[user_id]["gender"] = gender
        msg = "```text\n🛡️ CREATE HERO 🛡️\n\nMasukkan nama hero kamu dengan REPLY pesan ini:\n```"
        await callback.message.edit_text(msg)
        await callback.answer()

    @app.on_message(filters.reply & filters.text)
    async def hero_name_handler(client, message):
        user_id = str(message.from_user.id)
        if user_id not in CREATION_STATE:
            return
        state = CREATION_STATE[user_id]
        name = message.text.strip()
        slot = state["slot"]
        hero_class = state["class"]
        gender = state["gender"]
        base_stats = CLASS_STATS[hero_class].copy()
        new_hero = {
            "name": name,
            "class": hero_class,
            "gender": gender,
            "level": 1,
            "exp": 0,
            "hp": 100,
            "mp": 50,
            "base_stats": base_stats,
            "equipment": {}
        }
        db = load_hero_db()
        db.setdefault(user_id, {})
        db[user_id][slot] = new_hero
        save_hero_db(db)
        CREATION_STATE.pop(user_id, None)
        hero_preview = f"```text\n✅ HERO CREATED ✅\n\nSlot   : {slot}\nName   : {name}\nClass  : {hero_class}\nGender : {gender}\nLevel  : 1\nHP     : 100 💖\nMP     : 50 🔋\n```"
        await message.reply_text(hero_preview, reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("⬅ Back to My Hero Menu", callback_data="menu_B")]
        ]))

    # Hero delete callbacks
    @app.on_callback_query(filters.regex(r"delete_hero_"))
    async def delete_hero_cb(client, callback):
        user_id = str(callback.from_user.id)
        slot = callback.data.replace("delete_hero_", "")
        db = load_hero_db()
        user_heroes = db.get(user_id, {})
        if slot not in user_heroes:
            await callback.answer("Slot kosong.", show_alert=True)
            return
        name = user_heroes[slot]['name']
        msg = f"```text\n⚠️ DELETE HERO ⚠️\n\nApakah kamu yakin ingin menghapus hero:\n{name} (Slot {slot})?\n```"
        confirm_keyboard = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("✅ Ya, hapus", callback_data=f"confirm_delete_{slot}")],
            [types.InlineKeyboardButton("❌ Batal", callback_data="menu_B")]
        ])
        await callback.message.edit_text(msg, reply_markup=confirm_keyboard)
        await callback.answer()

    @app.on_callback_query(filters.regex(r"confirm_delete_"))
    async def confirm_delete_cb(client, callback):
        user_id = str(callback.from_user.id)
        slot = callback.data.replace("confirm_delete_", "")
        db = load_hero_db()
        user_heroes = db.get(user_id, {})
        if slot in user_heroes:
            name = user_heroes[slot]['name']
            del user_heroes[slot]
            db[user_id] = user_heroes
            save_hero_db(db)
            msg = f"```text\n✅ HERO DELETED ✅\n\n{name} telah dihapus dari Slot {slot}.\n```"
            await callback.message.edit_text(msg, reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("⬅ Back to My Hero Menu", callback_data="menu_B")]
            ]))
        else:
            await callback.answer("Slot kosong.", show_alert=True)

# ============================
# Add EXP from battle
# ============================
def add_exp_to_hero(user_id, slot, exp_amount):
    db = load_hero_db()
    user_heroes = db.get(user_id, {})
    hero = user_heroes.get(slot)
    if not hero:
        return
    hero["exp"] += exp_amount
    leveled = check_level_up(hero)
    save_hero_db(db)
    return leveled
