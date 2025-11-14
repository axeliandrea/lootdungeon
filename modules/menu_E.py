# Menu E - Lucky Wheel Integration untuk Web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def register_lucky_wheel_menu_E(app: Client):
    """Register Menu E - Lucky Wheel Web"""

    # ================================
    # COMMAND /E dan /menu_e
    # ================================
    @app.on_message(filters.private & filters.command(["E", "menu_e"]))
    async def lucky_wheel_menu_E(client, message):

        lucky_wheel_text = """
🎰 **LUCKY WHEEL MENU E** 🎰

Selamat datang di Lucky Wheel Online!

🌐 *Website Lucky Wheel:*
👉 https://lootdungeon.online

Fitur:
• Animasi spin ultra smooth
• Fair prize system
• Weekly bonus event
• Leaderboard

Klik tombol di bawah untuk membuka website!
        """

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 BUKA LUCKY WHEEL ONLINE", url="https://lootdungeon.online")],
            [InlineKeyboardButton("📊 STATISTIK LUCKY WHEEL", callback_data="luckywheel_stats")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="back_menu")]
        ])

        await message.reply_text(
            lucky_wheel_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    # ================================
    # CALLBACK: luckywheel_stats
    # ================================
    @app.on_callback_query(filters.regex("luckywheel_stats"))
    async def luckywheel_stats(client, callback_query):

        stats_text = """
📊 **LUCKY WHEEL STATS**

🎉 Jackpot hari ini: *3 kali*
💰 Total hadiah keluar: *12.450 coin*
🎟️ Tiket tersisa rata-rata: *58 tiket/user*

Klik tombol untuk main.
        """

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 MAIN SEKARANG", url="https://lootdungeon.online")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="back_menu")]
        ])

        await callback_query.edit_message_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    # ================================
    # CALLBACK: back_menu
    # ================================
    @app.on_callback_query(filters.regex("back_menu"))
    async def back_to_main_menu(client, callback_query):

        await callback_query.answer("Kembali ke menu utama...")

        await callback_query.edit_message_text(
            "⬅️ *Kembali ke menu utama*\n\n"
            "Silakan gunakan /activate untuk membuka tombol menu.",
            parse_mode="Markdown"
        )


__all__ = ["register_lucky_wheel_menu_E"]
