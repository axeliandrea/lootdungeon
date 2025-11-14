"""
Contoh Integrasi Lucky Wheel dengan Bot Telegram LootDungeon
File ini menunjukkan cara mengintegrasikan lucky wheel system ke dalam bot yang ada

Author: MiniMax Agent
"""

import logging
import sys
import os

# Tambahkan path ke utils.py yang sudah kita buat
sys.path.append('/workspace')  # Sesuaikan dengan lokasi file lucky_wheel_utils.py

from lucky_wheel_utils import (
    lucky_wheel_manager,
    handle_lucky_wheel_commands,
    get_lucky_wheel_info,
    get_user_lucky_wheel_status,
    buy_lucky_wheel_ticket,
    spin_lucky_wheel
)

# Import library telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    from telegram.constants import ParseMode
except ImportError:
    print("Install python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token (dari BotFather)
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"

class LootDungeonBot:
    """Bot utama LootDungeon dengan integrasi Lucky Wheel"""
    
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup semua command handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Lucky Wheel handlers
        self.application.add_handler(CommandHandler("spin", self.spin_command))
        self.application.add_handler(CommandHandler("luckywheel", self.spin_command))
        self.application.add_handler(CommandHandler("buyticket", self.buy_ticket_command))
        self.application.add_handler(CommandHandler("tiket", self.my_tickets_command))
        self.application.add_handler(CommandHandler("mytickets", self.my_tickets_command))
        self.application.add_handler(CommandHandler("prizes", self.prizes_command))
        self.application.add_handler(CommandHandler("hadiah", self.prizes_command))
        
        # Game commands (contoh)
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("inventory", self.inventory_command))
        self.application.add_handler(CommandHandler("battle", self.battle_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /start"""
        user = update.effective_user
        
        welcome_message = f"""
🎮 **Selamat datang di LootDungeon Bot!** 🎮

Halo {user.first_name}! Selamat datang di bot game RPG yang seru!

🎰 **LUCKY WHEEL SYSTEM**
• Spin lucky wheel untuk dapatkan hadiah amazing!
• /spin - Memutar lucky wheel
• /buyticket - Beli tiket (25 Fizz Coin)
• /prizes - Lihat daftar hadiah

🎮 **GAME COMMANDS**
• /profile - Lihat profil karakter
• /inventory - Lihat inventory
• /battle - Mulai battle

📚 **HELP**
• /help - Bantuan lengkap

Mari mulai petualangan Anda! 🗡️
        """
        
        # Keyboard untuk navigasi
        keyboard = [
            [InlineKeyboardButton("🎰 Lucky Wheel", callback_data="luckywheel")],
            [InlineKeyboardButton("🎮 Game Info", callback_data="gameinfo")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /help"""
        help_text = """
🤖 **LOOTDUNGEON BOT HELP** 🤖

🎰 **LUCKY WHEEL COMMANDS:**
• `/spin` atau `/luckywheel` - Spin lucky wheel (butuh 1 tiket)
• `/buyticket [jumlah]` - Beli tiket (25 Fizz Coin per tiket)
• `/tiket` atau `/mytickets` - Lihat status tiket dan saldo
• `/prizes` atau `/hadiah` - Lihat daftar hadiah lengkap
• Cooldown: 5 menit setiap spin
• Tiket tidak bisa ditukar kembali

🎮 **GAME COMMANDS:**
• `/profile` - Lihat profil dan statistik karakter
• `/inventory` - Lihat inventory dan item
• `/battle` - Mulai battle dengan monster

💡 **TIPS:**
• Gunakan lucky wheel untuk dapatkan Fizz Coin dan item rare
• Tiket lucky wheel bisa didapat dengan beli atau event
• Join grup untuk event khusus dan bonus!

🆘 **BUTUH BANTUAN?**
• Chat @support untuk bantuan teknis
• Ikuti channel @lootdungeon_news untuk update

Selamat bermain! 🎉
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def spin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /spin - Spin lucky wheel"""
        user_id = update.effective_user.id
        
        # Cek apakah user bisa spin
        can_spin, message = lucky_wheel_manager.can_spin(user_id)
        
        if not can_spin:
            await update.message.reply_text(message)
            return
        
        # Spin the wheel
        success, spin_message, prize = spin_lucky_wheel(user_id)
        
        if success and prize:
            # Buat animasi spin effect
            spin_text = "🎰 **SPINNING LUCKY WHEEL!** 🎰\n"
            spin_text += "🎡 *Spinning...* 🎡\n"
            spin_text += "⏳ *Mohon tunggu...* ⏳\n\n"
            await update.message.reply_text(spin_text, parse_mode=ParseMode.MARKDOWN)
            
            # Tampilkan hasil setelah delay
            result_text = f"""
🎉 **HASIL LUCKY WHEEL!** 🎉

{spin_message}

🏆 **HADIAH ANDA:**
{pizza.emoji if 'pizza' in locals() else '🎰'} **{prize.name}**
✨ {prize.description}
            """
            
            # Tambahkan efek jackpot
            if "JACKPOT" in prize.name:
                result_text += f"""

🎉🎉🎉 **JACKPOT! JACKPOT! JACKPOT!** 🎉🎉🎉
🎊 **CONGRATULATION!** 🎊
🎈 Anda berhasil mendapatkan JACKPOT terbesar! 🎈
            """
            
            # Keyboard untuk aksi selanjutnya
            keyboard = [
                [InlineKeyboardButton("🎫 Beli Tiket", callback_data="buyticket"),
                 InlineKeyboardButton("🎰 Spin Lagi", callback_data="spin")],
                [InlineKeyboardButton("📊 Status", callback_data="status"),
                 InlineKeyboardButton("🎁 Hadiah", callback_data="prizes")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(spin_message)
    
    async def buy_ticket_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /buyticket - Beli tiket lucky wheel"""
        user_id = update.effective_user.id
        
        # Parse jumlah tiket
        try:
            command_parts = update.message.text.split()
            amount = int(command_parts[1]) if len(command_parts) > 1 else 1
            
            if amount <= 0:
                await update.message.reply_text("❌ Jumlah tiket harus lebih dari 0!")
                return
            
            if amount > 50:  # Limit untuk menghindari spam
                await update.message.reply_text("❌ Maksimal beli 50 tiket sekaligus!")
                return
                
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Format: /buyticket [jumlah]\nContoh: /buyticket 5")
            return
        
        # Beli tiket
        message = buy_lucky_wheel_ticket(user_id, amount)
        
        # Keyboard untuk aksi selanjutnya
        keyboard = [
            [InlineKeyboardButton("🎰 Spin Sekarang!", callback_data="spin")],
            [InlineKeyboardButton("📊 Status", callback_data="status"),
             InlineKeyboardButton("🎁 Hadiah", callback_data="prizes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message + "\n\n🎯 Ingin langsung spin?",
            reply_markup=reply_markup
        )
    
    async def my_tickets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /mytickets - Lihat status tiket"""
        user_id = update.effective_user.id
        
        status = get_user_lucky_wheel_status(user_id)
        
        # Keyboard untuk navigasi
        keyboard = [
            [InlineKeyboardButton("🎫 Beli Tiket", callback_data="buyticket"),
             InlineKeyboardButton("🎰 Spin", callback_data="spin")],
            [InlineKeyboardButton("🎁 Hadiah", callback_data="prizes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def prizes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /prizes - Lihat daftar hadiah"""
        info = get_lucky_wheel_info()
        
        # Keyboard untuk aksi
        keyboard = [
            [InlineKeyboardButton("🎫 Beli Tiket", callback_data="buyticket"),
             InlineKeyboardButton("🎰 Spin", callback_data="spin")],
            [InlineKeyboardButton("📊 Status", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            info,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /profile - Lihat profil karakter"""
        user_id = update.effective_user.id
        user = update.effective_user
        
        # Ambil data dari lucky wheel system
        tickets = lucky_wheel_manager.get_user_tickets(user_id)
        user_data = lucky_wheel_manager.user_data.get(str(user_id), {})
        balance = user_data.get('balance', 0)
        hp = user_data.get('hp', 100)
        mp = user_data.get('mp', 50)
        
        profile_text = f"""
🎮 **PROFIL KARAKTER** 🎮

👤 **Nama:** {user.first_name}
🆔 **User ID:** {user_id}

💰 **EKONOMI:**
• Fizz Coin: {balance}
• Tiket Lucky Wheel: {tickets}

❤️ **STATISTIK:**
• HP: {hp}/999
• MP: {mp}/999

🎯 **LEVEL:** 1
⚔️ **ATTACK:** 10
🛡️ **DEFENSE:** 5
        """
        
        keyboard = [
            [InlineKeyboardButton("🎰 Lucky Wheel", callback_data="luckywheel")],
            [InlineKeyboardButton("🎫 Tiket", callback_data="status"),
             InlineKeyboardButton("🎁 Hadiah", callback_data="prizes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /inventory - Lihat inventory"""
        user_id = update.effective_user.id
        
        # Ambil data inventory dari lucky wheel system
        user_data = lucky_wheel_manager.user_data.get(str(user_id), {})
        tickets = user_data.get('tickets', 0)
        hp_potions = user_data.get('hp_potions', 0)
        mp_potions = user_data.get('mp_potions', 0)
        
        inventory_text = f"""
🎒 **INVENTORY** 🎒

🎫 **Tiket:** {tickets}
🧪 **Potion HP:** {hp_potions}
🧪 **Potion MP:** {mp_potions}

💰 **Item Currency:**
• Fizz Coin: {user_data.get('balance', 0)}
        """
        
        keyboard = [
            [InlineKeyboardButton("🎰 Lucky Wheel", callback_data="luckywheel")],
            [InlineKeyboardButton("🎫 Beli Tiket", callback_data="buyticket"),
             InlineKeyboardButton("🎰 Spin", callback_data="spin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(inventory_text, reply_markup=reply_markup)
    
    async def battle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /battle - Mulai battle"""
        battle_text = """
⚔️ **BATTLE SYSTEM** ⚔️

🦾 **Monster List:**
1. 🐺 Wolf (Easy) - Reward: 50 Fizz Coin
2. 🐗 Boar (Medium) - Reward: 100 Fizz Coin  
3. 🐉 Dragon (Hard) - Reward: 500 Fizz Coin

❓ **Pilih monster yang ingin ditantang:**
Ketik: /attack [nomor monster]

💡 **Tips:** Gunakan potion dari lucky wheel untuk healing!
        """
        
        keyboard = [
            [InlineKeyboardButton("🐺 Attack Wolf", callback_data="attack_1")],
            [InlineKeyboardButton("🐗 Attack Boar", callback_data="attack_2")],
            [InlineKeyboardButton("🐉 Attack Dragon", callback_data="attack_3")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(battle_text, reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        
        if action == "luckywheel":
            info = get_lucky_wheel_info()
            keyboard = [
                [InlineKeyboardButton("🎫 Beli Tiket", callback_data="buyticket"),
                 InlineKeyboardButton("🎰 Spin", callback_data="spin")],
                [InlineKeyboardButton("📊 Status", callback_data="status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        
        elif action == "buyticket":
            await query.edit_message_text(
                "🎫 **BELI TIKET LUCKY WHEEL** 🎫\n\n"
                "Gunakan command: /buyticket [jumlah]\n"
                "Contoh: /buyticket 5\n\n"
                "💰 **Harga:** 25 Fizz Coin per tiket"
            )
        
        elif action == "spin":
            # Trigger spin
            user_id = query.from_user.id
            
            can_spin, message = lucky_wheel_manager.can_spin(user_id)
            
            if not can_spin:
                await query.edit_message_text(message)
                return
            
            success, spin_message, prize = spin_lucky_wheel(user_id)
            
            if success and prize:
                result_text = f"""
🎉 **HASIL LUCKY WHEEL!** 🎉

{spin_message}

🏆 **HADIAH ANDA:**
🎰 **{prize.name}**
✨ {prize.description}
                """
                
                if "JACKPOT" in prize.name:
                    result_text += f"""

🎉🎉🎉 **JACKPOT!** 🎉🎉🎉
🎊 Congratulations! 🎊
                    """
                
                await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)
            else:
                await query.edit_message_text(spin_message)
        
        elif action == "status":
            user_id = query.from_user.id
            status = get_user_lucky_wheel_status(user_id)
            await query.edit_message_text(status, parse_mode=ParseMode.MARKDOWN)
        
        elif action == "prizes":
            info = get_lucky_wheel_info()
            await query.edit_message_text(info, parse_mode=ParseMode.MARKDOWN)
        
        elif action == "home":
            await self.start_command(update, context)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        message = update.message.text.lower()
        
        if "lucky wheel" in message or "luckywheel" in message:
            await self.prizes_command(update, context)
        elif "spin" in message:
            await self.spin_command(update, context)
        elif "ticket" in message or "tiket" in message:
            await self.my_tickets_command(update, context)
        else:
            # Responses for general conversation
            responses = [
                "🎮 Gunakan /help untuk bantuan!",
                "🎰 Spin lucky wheel dengan /spin!",
                "🎫 Beli tiket dengan /buyticket!",
                "🎮 Lihat profil dengan /profile!"
            ]
            
            import random
            response = random.choice(responses)
            await update.message.reply_text(response)
    
    def run(self):
        """Jalankan bot"""
        logger.info("🚀 Starting LootDungeon Bot with Lucky Wheel...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Fungsi utama"""
    try:
        # Buat dan jalankan bot
        bot = LootDungeonBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
