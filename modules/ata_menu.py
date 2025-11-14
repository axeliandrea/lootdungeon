# ATA/modules/ata_menu.py
from pyrogram import Client, filters, types
from modules import menu_register, menu_B, menu_C, menu_D, menu_H

OWNER_ID = 6395738130 

def main_menu_keyboard():
    return types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("📝 REGISTER", callback_data="menu_register"),
            types.InlineKeyboardButton("⚔️ MY HERO", callback_data="menu_B"),
            types.InlineKeyboardButton("🏰 DUNGEON", callback_data="menu_C")
        ],
        [
            types.InlineKeyboardButton("🎒 BAG", callback_data="menu_D"),
            types.InlineKeyboardButton("MENU E", callback_data="menu_E"),
            types.InlineKeyboardButton("MENU F", callback_data="menu_F")
        ],
        [
            types.InlineKeyboardButton("MENU G", callback_data="menu_G"),
            types.InlineKeyboardButton("ACHIEVEMENT", callback_data="menu_H"),
            types.InlineKeyboardButton("MENU I", callback_data="menu_I")
        ]
    ])


def register_handlers(app: Client, owner_id):
    print("[DEBUG][ata_menu] Modul ata_menu siap")

    # ===== COMMAND /activate =====
    @app.on_message(filters.private & filters.command("activate"))
    async def activate_cmd(client, message):
        text_msg = """```text
🎮 GAME MENU 🎮

Selamat datang di dunia petualangan!
Gunakan tombol di bawah untuk menjelajah menu:
```"""
        await message.reply_text(
            text=text_msg,
            reply_markup=main_menu_keyboard()
        )

    # ===== CALLBACK REGISTER MENU =====
    @app.on_callback_query(filters.regex(r"menu_register|menu_register_check"))
    async def register_cb(client, callback):
        await menu_register.register_handler(client, callback, owner_id)

    # ===== CALLBACK BACK TO MAIN MENU =====
    @app.on_callback_query(filters.regex("main_menu"))
    async def back_to_main(client, callback):
        text_msg = """```text
🎮 GAME MENU 🎮

Kembali ke menu utama.
Gunakan tombol di bawah untuk navigasi:
```"""
        await callback.message.edit_text(
            text=text_msg,
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()


    # ===== REGISTER MENU B (My Hero) HANDLER =====
    menu_B.register(app, owner_id)
    menu_C.register(app, owner_id)
    menu_D.register(app)



