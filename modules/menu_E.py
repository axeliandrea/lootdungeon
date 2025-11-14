from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from modules.lucky_wheel_utils import lucky_wheel_manager

def register_lucky_wheel_menu_E(app: Client):
    print("🔗 [DEBUG] Menu E registered...")

    # =====================================
    # FUNCTION untuk menampilkan menu E
    # =====================================
    async def send_menu_e(input_obj):
        if isinstance(input_obj, pyrogram.types.CallbackQuery):
            send_func = input_obj.message.edit_text
        else:
            send_func = input_obj.reply_text
    
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

    await send_func(text, reply_markup=keyboard)


        await send_func(text, reply_markup=keyboard)

    # =====================================
    # COMMAND /E dan /menu_e
    # =====================================
    @app.on_message(filters.private & filters.command(["E", "menu_e"]))
    async def open_menu_e(client, message):
        print("📨 [DEBUG] /E command triggered")
        await send_menu_e(message)
        print("✅ [DEBUG] Menu E displayed successfully")

    # =====================================
    # CALLBACK: STATISTIK
    # =====================================
    @app.on_callback_query(filters.regex(r"^E_STATS$"), group=-1)
    async def show_stats(client, callback_query):
        user_id = callback_query.from_user.id
        print(f"📌 [DEBUG] CALLBACK: E_STATS triggered for user {user_id}")

        stats_text = f"""
📊 **STATISTIK LUCKY WHEEL**
🎫 Tiket Anda: {lucky_wheel_manager.get_user_tickets(user_id)}
💰 Fizz Coin: {lucky_wheel_manager.user_data.get(str(user_id), {}).get('balance',0)}
✅ Siap Spin! Tekan tombol di bawah untuk memutar Lucky Wheel.
        """

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 SPIN SEKARANG", callback_data="SPIN_NOW")],
            [InlineKeyboardButton("⬅️ KEMBALI", callback_data="E_BACK")]
        ])

        await callback_query.answer()
        await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
        print("✅ [DEBUG] Statistik berhasil ditampilkan")

    # =====================================
    # CALLBACK: SPIN NOW
    # =====================================
    @app.on_callback_query(filters.regex("^SPIN_NOW$"), group=-1)
    async def spin_now(client, callback_query):
        user_id = callback_query.from_user.id
        print(f"🎰 [DEBUG] SPIN_NOW triggered for user {user_id}")

        can_spin, message_text = lucky_wheel_manager.can_spin(user_id)
        if not can_spin:
            await callback_query.answer(message_text, show_alert=True)
            return

        success, spin_message, prize = lucky_wheel_manager.spin_wheel(user_id)
        if success and prize:
            result_text = f"🎰 **LUCKY WHEEL SPINNED!** 🎰\n\n{spin_message}\n\n🏆 **HADIAH ANDA:**\n{prize.icon} **{prize.name}**\n✨ {prize.description}"
            if prize.prize_type.name == "JACKPOT":
                result_text += f"\n\n🎉🎉🎉 **JACKPOT!** 🎉🎉🎉\n🎊 Selamat! Anda mendapatkan jackpot terbesar! 🎊"
            await callback_query.message.edit_text(result_text)
            await callback_query.answer()
            print(f"✅ User {user_id} mendapatkan hadiah: {prize.name}")
        else:
            await callback_query.answer(spin_message, show_alert=True)

    # =====================================
    # CALLBACK: BACK ke menu utama
    # =====================================
    @app.on_callback_query(filters.regex("^E_BACK$"), group=-1)
    async def go_back(client, callback_query):
        print("📌 [DEBUG] CALLBACK: E_BACK triggered")

        back_text = "⬅️ Kamu kembali ke menu utama.\nSilahkan pilih menu:"
        main_menu_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧙‍♂️ My Hero", callback_data="MENU_B")],
            [InlineKeyboardButton("⚔️ Battle", callback_data="MENU_C")],
            [InlineKeyboardButton("🎒 Inventory", callback_data="MENU_D")],
            [InlineKeyboardButton("🎰 Lucky Wheel", callback_data="OPEN_E")]
        ])

        await callback_query.answer()
        await callback_query.message.edit_text(back_text, reply_markup=main_menu_keyboard)
        print("🔙 [DEBUG] User kembali ke menu utama")

    # =====================================
    # CALLBACK: OPEN_E (dari tombol main menu)
    # =====================================
    @app.on_callback_query(filters.regex("^OPEN_E$"), group=-1)
    async def open_menu_e_callback(client, callback_query):
        print("📨 [DEBUG] OPEN_E callback triggered")
        await callback_query.answer()
        await send_menu_e(callback_query)
        print("✅ [DEBUG] Menu E ditampilkan ulang via OPEN_E")
