# ATA/ATA/modules/menu_D.py 05:22
from pyrogram import types, filters
from modules.bag_utils import load_bag, save_bag

def format_bag_text(bag):
    lines = []
    # Fizz Coin
    lines.append(f"Fizz Coin: {bag.get('Fizz Coin',0)}\n")
    
    # Monster Drop
    lines.append("Monster Drop:")
    monster_drop = bag.get("Monster Drop", {})
    if monster_drop:
        for item, qty in monster_drop.items():
            lines.append(f"{item}: {qty}x")
    else:
        lines.append("  - (Empty)")

    # Equipment Drop
    lines.append("\nEquipment Drop:")
    equipment_drop = bag.get("Equipment Drop", {})
    if equipment_drop:
        for item, data in equipment_drop.items():
            lines.append(f"{item}: {data.get('qty',1)}x (not equipped)")
    else:
        lines.append("  - (Empty)")

    # Card Drop
    lines.append("\nCard Drop:")
    card_drop = bag.get("Card Drop", {})
    if card_drop:
        for item, qty in card_drop.items():
            lines.append(f"{item}: {qty}x")
    else:
        lines.append("  - (Empty)")

    return "```text\n" + "\n".join(lines) + "\n```"

def bag_menu_keyboard():
    keyboard = [
        [types.InlineKeyboardButton("⬅ Back to Main Menu", callback_data="main_menu")]
    ]
    return types.InlineKeyboardMarkup(keyboard)

def register(app):
    @app.on_callback_query(filters.regex("menu_D"))
    async def bag_menu_cb(client, callback):
        user_id = str(callback.from_user.id)
        # Ambil bag terbaru agar sinkron dengan battle_sim
        bag = load_bag(user_id)

        bag_text = format_bag_text(bag)
        await callback.message.edit_text(bag_text, reply_markup=bag_menu_keyboard())
        await callback.answer()
