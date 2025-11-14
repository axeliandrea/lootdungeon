# Menu E - Lucky Wheel Web (COMPLETELY FIXED VERSION)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_lucky_wheel_menu_E(app: Client):
    print("🔗 [DEBUG] Menu E registered...")

    # =====================================
    # COMMAND: /E dan /menu_e
    # =====================================
    @app.on_message(filters.private & filters.command(["E", "menu_e"]))
    async def open_menu_e(client, message):
        print("📨 [DEBUG] /E command triggered")

        text = (
            "🎰 **LUCKY WHEEL — MENU E** 🎰\n"
            "Selamat datang di Lucky Wheel Online!\n"
            "Tekan tombol di bawah untuk membuka submenu."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 BUKA WEBSITE", url="https://lootdungeon.online")],
            [InlineKeyboardButton("📊 STATISTIK", callback_data="E_STATS")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="E_BACK")]
        ])

        await message.reply_text(text, reply_markup=keyboard)
        print("✅ [DEBUG] Menu E displayed successfully")

    # =====================================
    # CALLBACK: STATISTIK
    # =====================================
    @app.on_callback_query(filters.regex("^E_STATS$"), group=-1)
    async def show_stats(client, callback_query):
        print("📌 [DEBUG] CALLBACK: E_STATS triggered")

        stats_text = (
            "📊 **STATISTIK LUCKY WHEEL**\n"
            "🎉 Jackpot hari ini: 3\n"
            "💰 Total hadiah keluar: 12.450 coin\n"
            "🎟️ Rata-rata tiket user: 58\n"
            "Klik tombol untuk main."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 MAIN SEKARANG", url="https://lootdungeon.online")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="E_BACK")]
        ])

        await callback_query.answer()  # hilangkan loading
        await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
        print("✅ [DEBUG] Statistik berhasil ditampilkan")

    # =====================================
    # CALLBACK: BACK
    # =====================================
    @app.on_callback_query(filters.regex("^E_BACK$"), group=-1)
    async def go_back(client, callback_query):
        print("📌 [DEBUG] CALLBACK: E_BACK triggered")

        back_text = (
            "⬅️ Kembali ke menu utama.\n"
            "Gunakan /activate untuk membuka tombol utama."
        )

        await callback_query.answer()
        await callback_query.message.edit_text(back_text)
        print("🔙 [DEBUG] User kembali ke menu utama")
