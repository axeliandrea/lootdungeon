# ATA/modules/menu_C.py #03:18
from pyrogram import types, filters
import asyncio
from modules.monster.battle_sim import battle_simulation
from modules.menu_B import load_hero_db, ACTIVE_SLOT  # gunakan database hero & slot aktif

# Nama floor dari 1 sampai 20
FLOOR_NAMES = {
    1: "🏞️ Spring Canyon 🏞️",
    2: "Spider Nest",
    3: "Abandoned Mine",
    4: "Haunted Forest",
    5: "Crystal Lake",
    6: "Dark Swamp",
    7: "Frozen Tundra",
    8: "Volcanic Crater",
    9: "Lost Ruins",
    10: "Sunken Temple",
    11: "Bandit Hideout",
    12: "Mystic Library",
    13: "Cursed Village",
    14: "Dragon Lair",
    15: "Ancient Tomb",
    16: "Shadow Fortress",
    17: "Twilight Tower",
    18: "Demon's Gate",
    19: "Eternal Plains",
    20: "Sky Castle"
}

def dungeon_keyboard():
    keyboard = []
    for i in range(1, 21, 3):
        row = []
        for j in range(i, i + 3):
            if j <= 20:
                floor_name = FLOOR_NAMES.get(j, f"Floor {j}")
                row.append(types.InlineKeyboardButton(f"{floor_name}", callback_data=f"dungeon_floor_{j}"))
        keyboard.append(row)
    keyboard.append([types.InlineKeyboardButton("⬅ Back", callback_data="main_menu")])
    return types.InlineKeyboardMarkup(keyboard)

def floor_menu_keyboard(floor):
    floor_name = FLOOR_NAMES.get(int(floor), f"Floor {floor}")
    keyboard = [
        [types.InlineKeyboardButton("⚔️ Find Monster", callback_data=f"find_monster_{floor}")],
        [types.InlineKeyboardButton("⬅ Back to Entrance", callback_data="menu_C")]
    ]
    return types.InlineKeyboardMarkup(keyboard)

def hero_slot_keyboard(user_id, floor, monster_name):
    """Keyboard untuk pilih hero slot sebelum battle"""
    keyboard = []
    for slot_num in range(1, 4):
        keyboard.append([types.InlineKeyboardButton(f"Hero Slot {slot_num}", callback_data=f"battle_start_{floor}_{monster_name}_{slot_num}")])
    keyboard.append([types.InlineKeyboardButton("⬅ Back to Monster", callback_data=f"find_monster_{floor}")])
    return types.InlineKeyboardMarkup(keyboard)

def register(app, owner_id):
    print("[DEBUG][menu_C] Modul Dungeon siap")

    # ===== CALLBACK MENU C =====
    @app.on_callback_query(filters.regex("menu_C"))
    async def menu_C_handler(client, callback):
        msg = """```text
🏰 DUNGEON MENU 🏰

Pilih floor yang ingin kamu masuki:
```"""
        await callback.message.edit_text(msg, reply_markup=dungeon_keyboard())
        await callback.answer()

    # ===== CALLBACK MASUK KE FLOOR =====
    @app.on_callback_query(filters.regex(r"dungeon_floor_"))
    async def dungeon_floor_handler(client, callback):
        floor = callback.data.replace("dungeon_floor_", "")
        floor_name = FLOOR_NAMES.get(int(floor), f"Floor {floor}")
        msg = f"""```text
{floor_name}

Kamu sekarang berada di {floor_name}.
Apa yang ingin kamu lakukan?
```"""
        await callback.message.edit_text(msg, reply_markup=floor_menu_keyboard(floor))
        await callback.answer()

    # ===== CALLBACK FIND MONSTER =====
    @app.on_callback_query(filters.regex(r"find_monster_"))
    async def find_monster_handler(client, callback):
        floor = callback.data.replace("find_monster_", "")
        user_id = str(callback.from_user.id)
    
        hero_db = load_hero_db()
        slot = ACTIVE_SLOT.get(user_id, "1")
        hero = hero_db.get(user_id, {}).get(slot)
        hero_level = hero.get("level", 1) if hero else 1
    
        try:
            floor_module = __import__(f"modules.monster.floor{floor}", fromlist=["handle_find_monster"])
        except Exception as e:
            await callback.message.edit_text(f"[DEBUG] Floor module error: {e}")
            return

        # Hapus pesan menu sebelumnya
        await callback.message.delete()
        # Efek roll monster
        roll_msg = await callback.message.reply_text("🔎 Mencari monster...")
        await asyncio.sleep(3)
    
        try:
            monster_data = floor_module.handle_find_monster(hero_level=hero_level)
        except Exception as e:
            await roll_msg.edit_text(f"[DEBUG] Floor module error saat ambil monster: {e}")
            return
    
        if not monster_data or "monster" not in monster_data:
            msg = "⚔️ FIND MONSTER ⚔️\n\nBelum ada monster di floor ini!"
            reply_markup = types.InlineKeyboardMarkup([ 
                [types.InlineKeyboardButton("⬅ Back to Floor Menu", callback_data=f"dungeon_floor_{floor}")]
            ])
            await roll_msg.edit_text(msg, reply_markup=reply_markup)
            return
    
        monster = monster_data["monster"]
        
        msg = (
            f"⚔️ Menemukan monster: {monster['name']} ⚔️\n"
            f"Level: {monster['level']}\n"
            "Apakah kamu ingin melawan monster ini?"
        )

        reply_markup = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("✅ YES", callback_data=f"choose_slot_{floor}_{monster['name']}")],
            [types.InlineKeyboardButton("⬅ Back to Floor Menu", callback_data=f"dungeon_floor_{floor}")]
        ])

        await roll_msg.edit_text(msg, reply_markup=reply_markup)
        await callback.answer()

    # ===== CALLBACK PILIH SLOT HERO =====
    @app.on_callback_query(filters.regex(r"choose_slot_"))
    async def choose_slot_handler(client, callback):
        data = callback.data.replace("choose_slot_", "").split("_")
        floor, monster_name = data[0], "_".join(data[1:])
        user_id = str(callback.from_user.id)

        msg = f"⚔️ Pilih slot hero untuk melawan {monster_name}:"
        await callback.message.edit_text(msg, reply_markup=hero_slot_keyboard(user_id, floor, monster_name))
        await callback.answer()

    # ===== CALLBACK START BATTLE =====
    @app.on_callback_query(filters.regex(r"battle_start_"))
    async def battle_start_handler(client, callback):
        if not callback.message:
            await callback.answer("Pesan tidak tersedia.", show_alert=True)
            return
    
        data = callback.data.replace("battle_start_", "").split("_")
        floor, monster_name, slot_num = data[0], "_".join(data[1:-1]), data[-1]
        user_id = str(callback.from_user.id)
    
        # Ambil hero dari slot yang diklik
        hero_db = load_hero_db()
        hero = hero_db.get(user_id, {}).get(slot_num)
        if not hero:
            hero = {"name": f"Hero-{user_id}", "hp": 20, "mp": 10, "atk": [2, 4]}
    
        # Ambil monster dari floor module
        try:
            floor_module = __import__(f"modules.monster.floor{floor}", fromlist=["handle_find_monster"])
            monster_data = floor_module.handle_find_monster()
            monster = monster_data.get("monster") if monster_data else None
            if not monster:
                await callback.message.edit_text("[DEBUG] Monster tidak tersedia di floor ini")
                return
        except Exception as e:
            await callback.message.edit_text(f"[DEBUG] Gagal ambil monster: {e}")
            return
    
        # Hapus pesan slot hero sebelumnya
        await callback.message.delete()
    
        # Langsung mulai battle
        await battle_simulation(client, callback.message, hero, monster, floor)
        await callback.answer()
