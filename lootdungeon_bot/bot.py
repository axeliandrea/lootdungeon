"""
Telegram Bot for LootDungeon
Handles all bot commands and interactions
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID
from database import Database

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Create player if not exists
    is_new = db.get_or_create_player(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    if is_new:
        welcome_text = f"""
🎮 **Welcome to LootDungeon!** 🎮

Hello {user.first_name}! 👋

You have successfully registered and received:
🎫 **10 Lucky Tickets** to start your adventure!

**Available Commands:**
/menu - Open game menu
/info - Your player info
/help - Game instructions

Good luck on your treasure hunt! 🍀
        """
    else:
        welcome_text = f"""
🎮 **Welcome back to LootDungeon!** 🎮

Hello {user.first_name}! 👋

Ready for more adventures?

**Available Commands:**
/menu - Open game menu  
/info - Your player info
/help - Game instructions
        """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main game menu"""
    user = update.effective_user
    player = db.get_player(user.id)
    
    if not player:
        await update.message.reply_text("❌ Please register first with /start")
        return
    
    # Create 3x2 inline keyboard
    keyboard = [
        [InlineKeyboardButton("📝 REGISTER", callback_data="register"),
         InlineKeyboardButton("🎰 LUCKY WHEEL", callback_data="lucky_wheel")],
        [InlineKeyboardButton("🎒 BAG", callback_data="bag"),
         InlineKeyboardButton("🏪 STORE", callback_data="store")],
        [InlineKeyboardButton("🔜 COMING SOON", callback_data="coming_soon1"),
         InlineKeyboardButton("🔜 COMING SOON", callback_data="coming_soon2")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = f"""
🎮 **LootDungeon Menu** 🎮

**Player Info:**
👤 Name: {player['first_name']}
🎫 Tickets: {player['tickets']}
💰 Coins: {player['coins']}

Choose your adventure:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    player = db.get_player(user.id)
    
    if not player:
        await query.edit_message_text("❌ Please register first with /start")
        return
    
    if query.data == "register":
        await query.edit_message_text(f"""
📝 **Player Registration**

✅ **Status:** Registered
👤 **Name:** {player['first_name']}
📅 **Joined:** {player['registered_at']}

**Your Stats:**
🎫 Tickets: {player['tickets']}
💰 Coins: {player['coins']}

You're all set! Use /menu to start playing! 🎮
        """, parse_mode='Markdown')
    
    elif query.data == "lucky_wheel":
        lucky_wheel_url = f"http://lootdungeon.online/luckywheel?user_id={user.id}"
        await query.edit_message_text(f"""
🎰 **Lucky Wheel** 🎰

**Current Status:**
🎫 Tickets: {player['tickets']}
💰 Coins: {player['coins']}

**How to Play:**
• Click the link below to open the Lucky Wheel
• Each spin costs 1 ticket
• Win amazing prizes!

🎲 **[SPIN NOW]({lucky_wheel_url})** 🎲

*Note: The wheel will open in your browser*
        """, parse_mode='Markdown', disable_web_page_preview=True)
    
    elif query.data == "bag":
        await show_bag(update, context)
    
    elif query.data == "store":
        await query.edit_message_text("""
🏪 **Coming Soon!** 🏪

The store is currently under development.
Stay tuned for amazing items and upgrades!

For now, collect items through the Lucky Wheel! 🎰
        """, parse_mode='Markdown')
    
    elif query.data == "coming_soon1":
        await query.edit_message_text("🔜 **Feature Coming Soon!**\n\nThis feature is currently being developed.\nStay tuned for updates! 🚀", parse_mode='Markdown')
    
    elif query.data == "coming_soon2":
        await query.edit_message_text("🔜 **Feature Coming Soon!**\n\nThis feature is currently being developed.\nStay tuned for updates! 🚀", parse_mode='Markdown')

async def show_bag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show player bag/inventory"""
    query = update.callback_query
    user = update.effective_user
    items = db.get_player_items(user.id)
    
    if not items:
        bag_text = """
🎒 **Your Bag** 🎒

Your bag is empty! 😔

Spin the Lucky Wheel to collect items! 🎰
        """
        keyboard = [[InlineKeyboardButton("🎰 Spin Lucky Wheel", callback_data="lucky_wheel")]]
    else:
        bag_text = "🎒 **Your Bag** 🎒\n\n"
        for item in items:
            bag_text += f"{item['emoji']} **{item['item_name']}** x{item['quantity']}\n"
        
        # Create sub menu
        keyboard = [
            [InlineKeyboardButton("🎒 View Items", callback_data="bag_view"),
             InlineKeyboardButton("🔄 Transfer", callback_data="transfer_menu")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(bag_text, reply_markup=reply_markup, parse_mode='Markdown')

async def bag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bag sub-menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    items = db.get_player_items(user.id)
    
    if query.data == "bag_view":
        if not items:
            await query.edit_message_text("🎒 Your bag is empty!\n\nSpin the Lucky Wheel to collect items! 🎰")
            return
        
        bag_text = "🎒 **Your Inventory** 🎒\n\n"
        for item in items:
            bag_text += f"{item['emoji']} **{item['item_name']}**\n"
            bag_text += f"   📊 Quantity: {item['quantity']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Bag", callback_data="bag")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bag_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == "transfer_menu":
        if not items:
            await query.edit_message_text("🎒 Your bag is empty!\n\nYou need items to transfer! 🎰")
            return
        
        # Show transfer instructions
        transfer_text = """
🔄 **Transfer Items** 🔄

To transfer items, please use the format:
`/transfer @username item_type quantity`

**Example:**
`/transfer @johndoe coin 5`
`/transfer @janedoe ticket 2`

**Available items to transfer:**
        """
        
        for item in items:
            transfer_text += f"• {item['emoji']} {item['item_name']} (x{item['quantity']})\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Bag", callback_data="bag")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(transfer_text, reply_markup=reply_markup, parse_mode='Markdown')

async def player_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed player information"""
    user = update.effective_user
    player = db.get_player(user.id)
    items = db.get_player_items(user.id)
    
    if not player:
        await update.message.reply_text("❌ Please register first with /start")
        return
    
    info_text = f"""
👤 **Player Information**

**Basic Info:**
• Name: {player['first_name']}
• Username: @{player['username'] or 'Not set'}
• Registered: {player['registered_at']}

**Stats:**
• 🎫 Tickets: {player['tickets']}
• 💰 Coins: {player['coins']}

**Inventory:**
        """
    
    if not items:
        info_text += "• (Empty - Spin the Lucky Wheel!)"
    else:
        for item in items:
            info_text += f"• {item['emoji']} {item['item_name']} x{item['quantity']}\n"
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def transfer_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle item transfer command"""
    user = update.effective_user
    args = context.args
    
    if len(args) != 3:
        await update.message.reply_text("""
❌ **Invalid format!**

**Usage:** `/transfer @username item_type quantity`

**Examples:**
• `/transfer @johndoe coin 5`
• `/transfer @janedoe ticket 2`

**Available items:**
• coin - Fizz Coins
• ticket - Lucky Tickets  
• potion - Potion HP 50
        """, parse_mode='Markdown')
        return
    
    try:
        target_username = args[0].replace('@', '')
        item_type = args[1]
        quantity = int(args[2])
        
        if quantity <= 0:
            await update.message.reply_text("❌ Quantity must be positive!")
            return
        
        # Find target user
        target_player = None
        # Note: In a real implementation, you'd need to search through all players
        # For now, this is a simplified version
        await update.message.reply_text("""
⚠️ **Transfer System Note**

The transfer system is currently simplified.
In production, you would need to:
1. Search for the target username in the database
2. Verify the user exists and is registered
3. Complete the transfer process

For now, transfers are handled through the bag interface.
Please contact the bot developer for assistance.
        """, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Invalid quantity! Please use a number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = """
🎮 **LootDungeon Help** 🎮

**Getting Started:**
1. Use `/start` to register
2. Use `/menu` to access game features
3. Click "Lucky Wheel" to spin and win prizes!

**Available Commands:**
• `/start` - Register as a new player
• `/menu` - Open the main game menu
• `/info` - View your player information
• `/bag` - View your inventory
• `/transfer @user item quantity` - Transfer items
• `/help` - Show this help message

**Lucky Wheel Prizes:**
• 💰 Fizz Coin 100 (5% chance)
• 🎫 Lucky Ticket 3pcs (90% chance)  
• 🧪 Potion HP 50 3pcs (4% chance)
• ☠️ Zonk (1% chance)

**Game Features:**
• Owner gets unlimited Lucky Wheel tickets
• All prizes automatically added to your bag
• View and manage your inventory anytime
• Transfer items to other players

Need more help? Contact the bot developer! 🚀
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def bag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bag via command"""
    # Create fake callback to reuse show_bag logic
    fake_query = type('MockQuery', (), {
        'data': 'bag',
        'edit_message_text': update.message.reply_text,
        'edit_message_caption': None,
        'answer': lambda *args, **kwargs: None
    })()
    
    # Manually call show_bag logic
    await show_bag(type('MockUpdate', (), {'callback_query': fake_query, 'effective_user': update.effective_user})(), context)

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("info", player_info))
    application.add_handler(CommandHandler("bag", bag_command))
    application.add_handler(CommandHandler("transfer", transfer_item))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(bag_callback, pattern="^bag_"))
    
    # Start the bot
    print("🤖 LootDungeon Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()