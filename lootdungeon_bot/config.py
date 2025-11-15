"""
Configuration file for LootDungeon Bot
"""
import os

# Bot Configuration
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
OWNER_ID = 6395738130

# Web Configuration  
WEBHOOK_URL = "http://lootdungeon.online/webhook"
WEB_PORT = 5000
WEB_HOST = "0.0.0.0"

# Database Configuration
DATABASE_PATH = "lootdungeon.db"

# Lucky Wheel Configuration
LUCKY_WHEEL_PRIZES = {
    "coin": {"emoji": "💰", "name": "Fizz Coin", "amount": 100, "rate": 5},
    "ticket": {"emoji": "🎫", "name": "Lucky Ticket", "amount": 3, "rate": 90},
    "potion": {"emoji": "🧪", "name": "Potion HP 50", "amount": 3, "rate": 4},
    "zonk": {"emoji": "☠️", "name": "Zonk", "amount": 1, "rate": 1}
}

# Game Settings
STARTING_TICKETS = 10
TICKET_COST_PER_SPIN = 1