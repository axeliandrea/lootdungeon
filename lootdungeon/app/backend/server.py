from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_ID = int(os.environ.get('TELEGRAM_GROUP_ID', '0'))
OWNER_ID = int(os.environ.get('OWNER_ID', '0'))

# Prizes for the roulette
PRIZES = ["Gold 100", "Silver 50", "Bronze 25", "Jackpot 1000", "Diamond", "Ruby", "Emerald", "Sapphire", "Pearl", "Lucky Star"]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Pydantic Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    tickets: int = 0
    points: int = 0
    total_spins: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TicketClaim(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message_id: int
    ticket_amount: int
    claimed_by: List[int] = []
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SpinHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    telegram_id: int
    username: Optional[str] = None
    prize: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SpinRequest(BaseModel):
    telegram_id: int

class SpinResponse(BaseModel):
    success: bool
    prize: Optional[str] = None
    remaining_tickets: int = 0
    message: str

class UserResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    tickets: int
    points: int
    total_spins: int

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Lucky Wheel Roulette API"}

@api_router.get("/user/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int):
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.post("/spin", response_model=SpinResponse)
async def spin_roulette(spin_request: SpinRequest):
    telegram_id = spin_request.telegram_id
    
    # Get user
    user = await db.users.find_one({"telegram_id": telegram_id})
    if not user:
        return SpinResponse(
            success=False,
            message="User not found. Please start the bot first.",
            remaining_tickets=0
        )
    
    # Check if user has tickets
    if user.get('tickets', 0) < 1:
        return SpinResponse(
            success=False,
            message="You don't have enough tickets. Buy or claim tickets first!",
            remaining_tickets=0
        )
    
    # Spin the wheel - random prize
    prize = random.choice(PRIZES)
    
    # Update user tickets and total spins
    await db.users.update_one(
        {"telegram_id": telegram_id},
        {
            "$inc": {"tickets": -1, "total_spins": 1},
            "$set": {"last_spin": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Save spin history
    spin_history = SpinHistory(
        telegram_id=telegram_id,
        username=user.get('username'),
        prize=prize
    )
    doc = spin_history.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.spin_history.insert_one(doc)
    
    # Send notification to Telegram group
    if TELEGRAM_BOT_TOKEN and TELEGRAM_GROUP_ID:
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            username_display = f"@{user.get('username')}" if user.get('username') else user.get('first_name', 'Someone')
            message = f"🎰 <b>LUCKY WHEEL RESULT!</b> 🎰\n\n"
            message += f"🎁 Prize: <b>{prize}</b>\n"
            message += f"👤 Winner: {username_display}\n"
            message += f"🎟️ Tickets left: {user.get('tickets', 0) - 1}"
            
            await bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}")
    
    return SpinResponse(
        success=True,
        prize=prize,
        remaining_tickets=user.get('tickets', 0) - 1,
        message=f"Congratulations! You won {prize}!"
    )

@api_router.get("/history/{telegram_id}")
async def get_spin_history(telegram_id: int, limit: int = 20):
    history = await db.spin_history.find(
        {"telegram_id": telegram_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for item in history:
        if isinstance(item['timestamp'], str):
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    
    return history

@api_router.get("/prizes")
async def get_prizes():
    return {"prizes": PRIZES}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram Bot Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Create or update user in database
    existing_user = await db.users.find_one({"telegram_id": user.id})
    if not existing_user:
        new_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            tickets=0,
            points=0
        )
        doc = new_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    else:
        # Update username if changed
        await db.users.update_one(
            {"telegram_id": user.id},
            {"$set": {"username": user.username, "first_name": user.first_name}}
        )
    
    welcome_message = (
        f"🎰 <b>Welcome to Lucky Wheel Roulette!</b> 🎰\n\n"
        f"👋 Hi {user.first_name}!\n\n"
        f"<b>Commands:</b>\n"
        f"🎟️ /mytickets - Check your tickets & points\n"
        f"💰 /buyticket [amount] - Buy tickets with points (25 points = 1 ticket)\n\n"
        f"<b>How to get tickets:</b>\n"
        f"• Claim from group giveaways\n"
        f"• Earn points by chatting in group (5 characters = 1 point)\n"
        f"• Buy with points\n\n"
        f"🌐 <b>Play now:</b> Visit the web app to spin the wheel!"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def mytickets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await db.users.find_one({"telegram_id": user.id})
    
    if not user_data:
        await update.message.reply_text("Please use /start first!")
        return
    
    message = (
        f"🎟️ <b>Your Stats</b>\n\n"
        f"👤 User: {user.first_name}\n"
        f"🎫 Tickets: <b>{user_data.get('tickets', 0)}</b>\n"
        f"⭐ Points: <b>{user_data.get('points', 0)}</b>\n"
        f"🎰 Total Spins: {user_data.get('total_spins', 0)}\n\n"
        f"💡 <i>25 points = 1 ticket</i>"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')

async def giveticket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if user is owner
    if user.id != OWNER_ID:
        await update.message.reply_text("⛔ Only the owner can use this command!")
        return
    
    # Check if in group
    if update.effective_chat.id != TELEGRAM_GROUP_ID:
        await update.message.reply_text("⛔ This command can only be used in the group!")
        return
    
    # Parse ticket amount
    try:
        ticket_amount = int(context.args[0]) if context.args else 1
        if ticket_amount < 1 or ticket_amount > 10:
            await update.message.reply_text("⚠️ Ticket amount must be between 1 and 10!")
            return
    except (ValueError, IndexError):
        ticket_amount = 1
    
    # Create inline keyboard
    keyboard = [[InlineKeyboardButton("🎟️ CLAIM TICKET", callback_data=f"claim_{ticket_amount}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"🎁 <b>TICKET GIVEAWAY!</b> 🎁\n\n"
        f"🎟️ Tickets: <b>{ticket_amount}</b>\n"
        f"⏰ Expires in: <b>1 minute</b>\n\n"
        f"👇 Click the button below to claim!"
    )
    
    sent_message = await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    # Save ticket claim info with expiry
    ticket_claim = TicketClaim(
        message_id=sent_message.message_id,
        ticket_amount=ticket_amount,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    doc = ticket_claim.model_dump()
    doc['expires_at'] = doc['expires_at'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.ticket_claims.insert_one(doc)
    
    # Schedule expiry
    await asyncio.sleep(60)
    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=sent_message.message_id,
            text=f"🎁 <b>TICKET GIVEAWAY!</b> 🎁\n\n🎟️ Tickets: <b>{ticket_amount}</b>\n❌ <b>EXPIRED</b>",
            parse_mode='HTML'
        )
    except:
        pass

async def buyticket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Parse ticket amount
    try:
        ticket_amount = int(context.args[0]) if context.args else 1
        if ticket_amount < 1:
            await update.message.reply_text("⚠️ Ticket amount must be at least 1!")
            return
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ Usage: /buyticket [amount]\nExample: /buyticket 2")
        return
    
    # Calculate points needed (25 points per ticket)
    points_needed = ticket_amount * 25
    
    # Get user data
    user_data = await db.users.find_one({"telegram_id": user.id})
    if not user_data:
        await update.message.reply_text("Please use /start first!")
        return
    
    current_points = user_data.get('points', 0)
    
    if current_points < points_needed:
        await update.message.reply_text(
            f"❌ Not enough points!\n\n"
            f"You have: <b>{current_points}</b> points\n"
            f"You need: <b>{points_needed}</b> points\n\n"
            f"💡 Keep chatting in the group to earn points!\n"
            f"<i>(5 characters = 1 point)</i>",
            parse_mode='HTML'
        )
        return
    
    # Deduct points and add tickets
    await db.users.update_one(
        {"telegram_id": user.id},
        {
            "$inc": {
                "points": -points_needed,
                "tickets": ticket_amount
            }
        }
    )
    
    new_points = current_points - points_needed
    new_tickets = user_data.get('tickets', 0) + ticket_amount
    
    await update.message.reply_text(
        f"✅ <b>Purchase Successful!</b>\n\n"
        f"🎟️ Tickets bought: <b>{ticket_amount}</b>\n"
        f"💰 Points spent: <b>{points_needed}</b>\n\n"
        f"<b>New Balance:</b>\n"
        f"🎫 Tickets: <b>{new_tickets}</b>\n"
        f"⭐ Points: <b>{new_points}</b>",
        parse_mode='HTML'
    )

async def claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    callback_data = query.data
    
    # Parse ticket amount from callback data
    try:
        ticket_amount = int(callback_data.split('_')[1])
    except:
        await query.answer("Invalid claim!", show_alert=True)
        return
    
    # Get ticket claim info
    ticket_claim = await db.ticket_claims.find_one({"message_id": query.message.message_id})
    
    if not ticket_claim:
        await query.answer("This giveaway has expired!", show_alert=True)
        return
    
    # Check if expired
    expires_at = datetime.fromisoformat(ticket_claim['expires_at']) if isinstance(ticket_claim['expires_at'], str) else ticket_claim['expires_at']
    if datetime.now(timezone.utc) > expires_at:
        await query.answer("This giveaway has expired!", show_alert=True)
        return
    
    # Check if user already claimed
    if user.id in ticket_claim.get('claimed_by', []):
        await query.answer("You already claimed this!", show_alert=True)
        return
    
    # Create or update user
    existing_user = await db.users.find_one({"telegram_id": user.id})
    if not existing_user:
        new_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            tickets=ticket_amount,
            points=0
        )
        doc = new_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    else:
        await db.users.update_one(
            {"telegram_id": user.id},
            {"$inc": {"tickets": ticket_amount}}
        )
    
    # Add user to claimed list
    await db.ticket_claims.update_one(
        {"message_id": query.message.message_id},
        {"$push": {"claimed_by": user.id}}
    )
    
    await query.answer(f"✅ You claimed {ticket_amount} ticket(s)!", show_alert=True)
    
    # Notify in chat
    username_display = f"@{user.username}" if user.username else user.first_name
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"🎉 {username_display} claimed {ticket_amount} ticket(s)!"
    )

async def track_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only track in the group
    if update.effective_chat.id != TELEGRAM_GROUP_ID:
        return
    
    # Don't track bot messages
    if update.effective_user.is_bot:
        return
    
    user = update.effective_user
    message_text = update.message.text or ""
    
    # Calculate points: 5 characters = 1 point
    char_count = len(message_text)
    points_earned = char_count // 5
    
    if points_earned > 0:
        # Create or update user
        existing_user = await db.users.find_one({"telegram_id": user.id})
        if not existing_user:
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                tickets=0,
                points=points_earned
            )
            doc = new_user.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.users.insert_one(doc)
        else:
            await db.users.update_one(
                {"telegram_id": user.id},
                {"$inc": {"points": points_earned}}
            )

# Initialize Telegram Bot
async def init_telegram_bot():
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("mytickets", mytickets_command))
    application.add_handler(CommandHandler("giveticket", giveticket_command))
    application.add_handler(CommandHandler("buyticket", buyticket_command))
    application.add_handler(CallbackQueryHandler(claim_callback, pattern="^claim_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_points))
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Telegram bot started successfully")

@app.on_event("startup")
async def startup_event():
    # Start Telegram bot
    asyncio.create_task(init_telegram_bot())
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
