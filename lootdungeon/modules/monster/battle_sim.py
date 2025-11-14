# ATA/modules/monster/battle_sim.py
import random
import asyncio
import json
import os
from pyrogram import types
from modules.menu_B import load_hero_db, save_hero_db, ACTIVE_SLOT, CLASS_STATS, check_level_up
from modules.bag_utils import load_bag, save_bag
from modules.monster import floor1  # floor1 import langsung

# =================== Achievement DB ===================
ACHIEVEMENT_DB = "ATA/data/achievement_db.json"

def load_achievement_db():
    if not os.path.exists(ACHIEVEMENT_DB):
        return {}
    with open(ACHIEVEMENT_DB, "r") as f:
        return json.load(f)

def save_achievement_db(db):
    with open(ACHIEVEMENT_DB, "w") as f:
        json.dump(db, f, indent=2)

def update_achievement(user_id, monster_name=None, card_name=None):
    db = load_achievement_db()
    user_data = db.get(user_id, {"monster_kills": {}, "cards_collected": {}})

    if monster_name:
        user_data["monster_kills"][monster_name] = user_data["monster_kills"].get(monster_name, 0) + 1
    if card_name:
        user_data["cards_collected"][card_name] = user_data["cards_collected"].get(card_name, 0) + 1

    db[user_id] = user_data
    save_achievement_db(db)
# ======================================================

FLOOR_MODULES = {1: floor1}

async def battle_simulation(client, message, hero_override=None, monster=None, floor=1):
    user_id = str(message.chat.id)
    hero_db = load_hero_db()
    user_data = hero_db.get(user_id, {})
    bag = load_bag(user_id)
    for key in ["Fizz Coin", "Monster Drop", "Equipment Drop", "Card Drop"]:
        if key not in bag:
            bag[key] = 0 if key == "Fizz Coin" else {}

    # Ambil hero
    if hero_override:
        hero = hero_override
        slot = "_override"
        for k, h in user_data.items():
            if isinstance(h, dict) and h.get("name") == hero.get("name"):
                slot = k
                hero = h
                break
    else:
        slot = ACTIVE_SLOT.get(user_id)
        if not slot or slot not in user_data:
            if user_data:
                slot = sorted(user_data.keys())[0]
                ACTIVE_SLOT[user_id] = slot
            else:
                await message.reply("⚠️ Hero belum dibuat.")
                return
        hero = user_data.get(slot, {})

    if not hero.get("name") or not hero.get("class"):
        await message.reply("⚠️ Data hero kosong.")
        return

    hero_name = hero.get("name")
    hero_hp = hero.get("hp", 100)
    hero_mp = max(0, hero.get("mp", 50) - 2)  # Pakai 2 MP per battle
    hero_class = hero.get("class")
    hero_level = hero.get("level", 1)
    hero_base_stats = hero.get("base_stats", CLASS_STATS.get(hero_class, CLASS_STATS["Swordman"]).copy())
    hero_atk = hero.get("atk", [2, 4])
    if not isinstance(hero_atk, list) or len(hero_atk) != 2:
        hero_atk = [2, 4]

    # Pilih monster
    floor_module = FLOOR_MODULES.get(floor, floor1)
    if not monster:
        monster_data = floor_module.handle_find_monster(hero_level=hero_level)
        if not monster_data:
            await message.reply("⚔️ FIND MONSTER ⚔️\n\nBelum ada monster di floor ini!")
            return
        monster = monster_data.get("monster")

    monster_name = monster.get("name", "Monster")
    monster_hp = monster.get("hp", 10)
    monster_atk = monster.get("atk", [1, 3])
    monster_level = monster.get("level", 1)
    base_exp = monster.get("base_exp", 1)
    base_coin = monster.get("base_coin", 1)
    drop_chance = monster.get("chance", 0)

    # Hitung reward
    if hero_level == monster_level:
        exp_gain = base_exp
        coin_gain = base_coin
    elif hero_level < monster_level:
        multiplier = 1 + 0.5 * (monster_level - hero_level)
        exp_gain = base_exp * multiplier
        coin_gain = base_coin * multiplier
    else:
        multiplier = max(0, 1 - 0.25 * (hero_level - monster_level))
        exp_gain = base_exp * multiplier
        coin_gain = base_coin * multiplier

    exp_gain = round(exp_gain, 2)
    coin_gain = round(coin_gain, 2)

    battle_text = f"⚔️ {hero_name} vs {monster_name} ⚔️\nMP digunakan: 2 (sisa: {hero_mp})"
    battle_msg = await message.reply(f"```text\n{battle_text}```")

    while hero_hp > 0 and monster_hp > 0:
        dmg_hero = random.randint(*hero_atk)
        monster_hp = max(0, monster_hp - dmg_hero)
        battle_text += f"\n{hero_name} menyerang {monster_name} → {dmg_hero} dmg (HP: {monster_hp})"
        await battle_msg.edit_text(f"```text\n{battle_text}```")
        await asyncio.sleep(random.uniform(0.5, 1.0))
        if monster_hp <= 0:
            break

        dmg_monster = random.randint(*monster_atk)
        hero_hp = max(0, hero_hp - dmg_monster)
        battle_text += f"\n{monster_name} menyerang {hero_name} → {dmg_monster} dmg (HP: {hero_hp})"
        await battle_msg.edit_text(f"```text\n{battle_text}```")
        await asyncio.sleep(random.uniform(0.5, 1.0))

    # Setelah battle
    if monster_hp <= 0:
        hero["exp"] = hero.get("exp", 0) + exp_gain
        bag["Fizz Coin"] += int(coin_gain)

        leveled = check_level_up(hero)
        if leveled:
            battle_text += f"\n🎉 {hero_name} naik level! Sekarang level {hero['level']}"

        # ===== UPDATE ACHIEVEMENT (Monster Kill) =====
        update_achievement(user_id, monster_name=monster_name)
        battle_text += f"\n🏆 Telah membunuh {monster_name}!"

        # Drop
        drop_roll = random.randint(1, 100)
        if drop_roll <= drop_chance:
            item_type = random.choice(["Card Drop", "Monster Drop", "Equipment Drop"])
            if item_type == "Equipment Drop":
                item_name = floor_module.drop_floor1_equipment(monster)
                if item_name:
                    bag["Equipment Drop"][item_name] = bag["Equipment Drop"].get(item_name, {"qty":0,"equipped":False})
                    bag["Equipment Drop"][item_name]["qty"] += 1
                    battle_text += f"\n🎁 Monster menjatuhkan: {item_name} (Equipment)"
            elif item_type == "Card Drop":
                item_name = f"{monster_name}_card"
                bag["Card Drop"][item_name] = bag["Card Drop"].get(item_name, 0) + 1
                update_achievement(user_id, card_name=item_name)
                battle_text += f"\n🎁 Monster menjatuhkan: 🃏 {item_name}"
            elif item_type == "Monster Drop":
                item_name = f"{monster_name}_Drop"
                bag["Monster Drop"][item_name] = bag["Monster Drop"].get(item_name, 0) + 1
                battle_text += f"\n🎁 Monster menjatuhkan: {item_name}"
    else:
        lost_exp = int(hero.get("exp", 0) * 0.3)
        hero["exp"] = max(0, hero.get("exp", 0) - lost_exp)
        lost_coin = int(bag.get("Fizz Coin", 0) * 0.005)
        bag["Fizz Coin"] = max(0, bag["Fizz Coin"] - lost_coin)
        battle_text += f"\n💀 {hero_name} kalah...\nEXP berkurang {lost_exp}, Fizz Coin berkurang {lost_coin}"

    # Update hero & bag
    hero["hp"] = hero_hp
    hero["mp"] = hero_mp
    hero["base_stats"] = hero_base_stats
    user_data[slot] = hero
    hero_db[user_id] = user_data
    save_hero_db(hero_db)
    save_bag(user_id, bag)

    # Tombol back
    reply_markup = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("⬅ Back to Floor Menu", callback_data=f"dungeon_floor_{floor}")]
    ])
    await battle_msg.edit_text(f"```text\n{battle_text}```", reply_markup=reply_markup)
