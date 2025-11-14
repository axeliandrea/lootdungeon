# Menu E - Lucky Wheel Web (SUPER FIXED VERSION)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_lucky_wheel_menu_E(app: Client):
    print("🔗 Menu E registered...")  # DEBUG

    # =====================================
    # COMMAND: /E dan /menu_e
    # =====================================
    @app.on_message(filters.private & filters.command(["E", "menu_e"]))
    async def open_menu_e(client, message):
        print("📨 /E command triggered")  # DEBUG

        text = """
🎰 **LUCKY WHEEL — MENU E** 🎰

Selamat datang di Lucky Wheel Online!
Tekan tombol di bawah untuk membuka submenu.
        """

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 BUKA WEBSITE", url="https://lootdungeon.online")],
            [InlineKeyboardButton("📊 STATISTIK", callback_data="E_STATS")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="E_BACK")]
        ])

        await message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

    # =====================================
    # CALLBACK: STATISTIK
    # =====================================
    @app.on_callback_query(filters.regex("^E_STATS$"), group=-1)
    async def show_stats(client, callback_query):
        print("📌 CALLBACK: E_STATS")  # DEBUG

        stats_text = """
📊 **STATISTIK LUCKY WHEEL**

🎉 Jackpot hari ini: 3
💰 Total hadiah keluar: 12.450 coin
🎟️ Rata-rata tiket user: 58

Klik tombol untuk main.
        """

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 MAIN SEKARANG", url="https://lootdungeon.online")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="E_BACK")]
        ])

        await callback_query.edit_message_text(stats_text, reply_markup=keyboard, parse_mode="Markdown")

    # =====================================
    # CALLBACK: BACK
    # =====================================
    @app.on_callback_query(filters.regex("^E_BACK$"), group=-1)
    async def go_back(client, callback_query):
        print("📌 CALLBACK: E_BACK")  # DEBUG

        await callback_query.edit_message_text(
            "⬅️ Kembali ke menu utama.\nGunakan /activate untuk membuka tombol utama.",
            parse_mode="Markdown"
        )
