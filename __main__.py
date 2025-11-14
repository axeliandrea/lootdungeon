# __main__.py - FIXED WITH MENU E REGISTRATION
import os
import sys
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters

# Import modules - PENTING: Import sebelum sys.path
from modules import ata_menu, menu_H, menu_B, menu_C, menu_D, menu_E, cekid  # ← TAMBAHKAN menu_E!

# Import lucky wheel functions
from modules.lucky_wheel_utils import (
    lucky_wheel_manager,
    spin_lucky_wheel,
    buy_lucky_wheel_ticket,
    get_user_lucky_wheel_status,
    get_lucky_wheel_info
)

# ==========================================================
# LOAD ENV
# ==========================================================
load_dotenv()
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

if not all([API_ID, API_HASH, BOT_TOKEN, OWNER_ID]):
    print("⚠️ Pastikan semua variabel .env sudah benar")
    exit(1)

# ==========================================================
# INIT BOT
# ==========================================================
app = Client("MainBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ==========================================================
# REGISTER HANDLERS MODULAR
# ==========================================================
ata_menu.register_handlers(app, OWNER_ID)
cekid.register_handlers(app)
menu_H.register(app)
menu_E.register_lucky_wheel_menu_E(app)  # ← TAMBAHKAN REGISTRASI MENU E!

# ==========================================================
# LUCKY WHEEL COMMAND HANDLERS (BOT COMMANDS)
# ==========================================================

# Command: /spin - Spin lucky wheel (bot command)
@app.on_message(filters.private & filters.command(["spin", "luckywheel"]))
async def spin_lucky_wheel_command(client, message):
    user_id = message.from_user.id
    
    # Cek apakah bisa spin
    can_spin, message_text = lucky_wheel_manager.can_spin(user_id)
    
    if not can_spin:
        await message.reply_text(message_text)
        return
    
    # Spin lucky wheel
    success, spin_message, prize = spin_lucky_wheel(user_id)
    
    if success and prize:
        result_text = f"🎰 **LUCKY WHEEL SPINNED!** 🎰\n\n{spin_message}\n\n🏆 **HADIAH ANDA:**\n{prize.icon} **{prize.name}**\n✨ {prize.description}"
        
        # Tambahkan efek jackpot
        if "JACKPOT" in prize.name:
            result_text += f"\n\n🎉🎉🎉 **JACKPOT! JACKPOT! JACKPOT!** 🎉🎉🎉\n🎊 Congratulations! Anda mendapatkan jackpot terbesar! 🎊"
        
        await message.reply_text(result_text, parse_mode='Markdown')
    else:
        await message.reply_text(spin_message)

# Command: /buyticket [jumlah] - Beli tiket
@app.on_message(filters.private & filters.command("buyticket"))
async def buy_ticket_command(client, message):
    user_id = message.from_user.id
    
    try:
        # Parse jumlah tiket
        command_parts = message.text.split()
        amount = int(command_parts[1]) if len(command_parts) > 1 else 1
        
        if amount <= 0:
            await message.reply_text("❌ Jumlah tiket harus lebih dari 0!")
            return
        
        if amount > 50:  # Limit untuk menghindari spam
            await message.reply_text("❌ Maksimal beli 50 tiket sekaligus!")
            return
            
    except (ValueError, IndexError):
        await message.reply_text("❌ Format: /buyticket [jumlah]\nContoh: /buyticket 5")
        return
    
    # Beli tiket
    result_message = buy_lucky_wheel_ticket(user_id, amount)
    await message.reply_text(result_message)

# Command: /tiket atau /mytickets - Lihat status tiket
@app.on_message(filters.private & filters.command(["tiket", "mytickets"]))
async def my_tickets_command(client, message):
    user_id = message.from_user.id
    status = get_user_lucky_wheel_status(user_id)
    await message.reply_text(status, parse_mode='md')

# Command: /prizes atau /hadiah - Lihat daftar hadiah
@app.on_message(filters.private & filters.command(["prizes", "hadiah"]))
async def prizes_command(client, message):
    info = get_lucky_wheel_info()
    await message.reply_text(info, parse_mode='md')

# ==========================================================
# COMMAND /restart (OWNER only)
# ==========================================================
@app.on_message(filters.private & filters.command("restart") & filters.user(OWNER_ID))
async def restart_bot(client, message):
    await message.reply_text("♻️ Bot sedang restart...")
    print("🔄 Restart bot oleh OWNER")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ==========================================================
# COMMAND /help
# ==========================================================
@app.on_message(filters.private & filters.command("help"))
async def help_command(client, message):
    help_text = (
        "❓ *HELP MENU*\n\n"
        "🎰 **LUCKY WHEEL WEB (Menu E):**\n"
        "• /E - Buka Lucky Wheel Online (lootdungeon.online)\n"
        "• /menu_e - Alias untuk Lucky Wheel Web\n\n"
        "🎮 **LUCKY WHEEL BOT:**\n"
        "• /spin - Spin lucky wheel (butuh 1 tiket)\n"
        "• /buyticket [jumlah] - Beli tiket (25 Fizz Coin)\n"
        "• /tiket - Lihat status tiket\n"
        "• /prizes - Lihat daftar hadiah\n\n"
        "🤖 **BOT:**\n"
        "• /restart → Restart bot (hanya OWNER)\n"
        "• /help → Tampilkan informasi ini\n"
        "• /getid → Cek User ID, Chat ID, atau Channel ID\n"
        "• /activate → Tampilkan menu tombol REGISTER / MENU B–I"
    )
    await message.reply_text(help_text, parse_mode='md')

# ==========================================================
# ADMIN FUNCTIONS (OWNER ONLY)
# ==========================================================

# Admin menambah tiket untuk user
@app.on_message(filters.private & filters.command("addticket") & filters.user(OWNER_ID))
async def admin_add_ticket_command(client, message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.reply_text("❌ Format: /addticket [user_id] [jumlah_tiket]")
            return
        
        target_user_id = int(command_parts[1])
        amount = int(command_parts[2])
        
        # Tambah tiket via lucky wheel manager
        success = lucky_wheel_manager.admin_add_tickets(target_user_id, amount)
        
        if success:
            await message.reply_text(f"✅ Berhasil menambah {amount} tiket untuk user {target_user_id}")
        else:
            await message.reply_text("❌ Gagal menambah tiket")
            
    except (ValueError, IndexError):
        await message.reply_text("❌ Format: /addticket [user_id] [jumlah_tiket]")
        return

# Admin update chance prize
@app.on_message(filters.private & filters.command("updatechance") & filters.user(OWNER_ID))
async def admin_update_chance_command(client, message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.reply_text("❌ Format: /updatechance [nama_hadiah] [persentase_baru]\nContoh: /updatechance \"JACKPOT Fizz Coin 5000\" 5.0")
            return
        
        prize_name = command_parts[1]
        new_chance = float(command_parts[2])
        
        # Update chance
        success = lucky_wheel_manager.update_prize_chance(prize_name, new_chance)
        
        if success:
            await message.reply_text(f"✅ Berhasil update chance {prize_name} menjadi {new_chance}%")
        else:
            await message.reply_text(f"❌ Hadiah {prize_name} tidak ditemukan")
            
    except (ValueError, IndexError):
        await message.reply_text("❌ Format: /updatechance [nama_hadiah] [persentase_baru]")

# ==========================================================
# DEBUG PRIVATE MESSAGE
# ==========================================================
@app.on_message(filters.private, group=99)
async def debug_message(client, message):
    if message.text and message.text.startswith("/"):
        return
    user_id = message.from_user.id if message.from_user else "Unknown"
    username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else str(user_id)
    print(f"[DEBUG] Pesan dari {username}: {message.text}")

# ==========================================================
# RUN BOT
# ==========================================================
if __name__ == "__main__":
    print("🚀 Bot utama aktif dengan Lucky Wheel!")
    print("🎰 Lucky Wheel Web (Menu E):")
    print("   /E - Lucky Wheel Online di lootdungeon.online")
    print("🎮 Lucky Wheel Bot Commands:")
    print("   /spin - Spin lucky wheel")
    print("   /buyticket [jumlah] - Beli tiket")
    print("   /tiket - Lihat status")
    print("   /prizes - Lihat hadiah")

    app.run()

