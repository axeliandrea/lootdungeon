# 🎮 LootDungeon Bot System

Telegram Bot dengan Lucky Wheel terintegrasi web browser untuk game reward system.

## 🌟 Features

- **Telegram Bot Interface** dengan inline keyboard menu 3x2
- **Lucky Wheel Web Interface** dengan animasi spinning yang menarik
- **Reward System** dengan 4 jenis hadiah dengan rate chance yang berbeda
- **Inventory Management** (BAG) untuk menyimpan semua hadiah
- **Item Transfer** sistem untuk player-to-player transfer
- **Owner Privileges** dengan unlimited Lucky Wheel tickets
- **SQLite Database** untuk persistent data storage

## 🎰 Lucky Wheel Prizes

| Prize | Emoji | Rate | Quantity |
|-------|-------|------|----------|
| Fizz Coin | 💰 | 5% | 100 |
| Lucky Ticket | 🎫 | 90% | 3 |
| Potion HP 50 | 🧪 | 4% | 3 |
| Zonk | ☠️ | 1% | 1 |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the System

```bash
python run.py
```

Bot akan berjalan di background dan web server di port 5000.

### 3. Set Webhook (Production)

Untuk production, set webhook Telegram ke domain Anda:

```bash
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://yourdomain.com/webhook"}'
```

## 📁 File Structure

```
lootdungeon_bot/
├── bot.py              # Main Telegram bot logic
├── web_app.py          # Flask web application
├── run.py              # Main runner (runs both bot and web)
├── database.py         # SQLite database management
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── templates/
│   └── lucky_wheel.html # Lucky wheel web interface
└── lootdungeon.db      # SQLite database (auto-created)
```

## ⚙️ Configuration

Edit `config.py` untuk customisasi:

```python
# Bot Configuration
BOT_TOKEN = "your_bot_token_here"
OWNER_ID = 6395738130  # Owner dengan unlimited tickets

# Web Configuration
WEBHOOK_URL = "http://yourdomain.com/webhook"
WEB_PORT = 5000

# Lucky Wheel Settings
STARTING_TICKETS = 10
TICKET_COST_PER_SPIN = 1
```

## 📱 Bot Commands

### Player Commands
- `/start` - Register sebagai player baru
- `/menu` - Buka menu game utama
- `/info` - Lihat informasi player
- `/bag` - Buka inventory/bag
- `/transfer @username item quantity` - Transfer item
- `/help` - Bantuan lengkap

### Menu Structure
```
[REGISTER] [LUCKY WHEEL] [BAG]
[STORE]  [COMING SOON] [COMING SOON]
```

### BAG Sub-Menu
- **BAG** - Tampilkan semua items player
- **Transfer** - Menu transfer items ke player lain

## 🌐 Web Interface

Lucky Wheel dapat diakses via web browser dengan URL:
`http://yourdomain.com/luckywheel?user_id={telegram_user_id}`

### Features Web Interface:
- **Animasi Spinning Wheel** yang smooth
- **Real-time Prize Display** dengan efek visual
- **Player Stats** (tickets dan coins)
- **Responsive Design** untuk mobile dan desktop
- **Automatic Inventory Update** setelah spin

## 🗄️ Database Schema

### Players Table
```sql
CREATE TABLE players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tickets INTEGER DEFAULT 10,
    coins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_type TEXT,
    item_name TEXT,
    emoji TEXT,
    quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES players (user_id)
);
```

### Spin History Table
```sql
CREATE TABLE spin_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    prize_type TEXT,
    prize_name TEXT,
    prize_emoji TEXT,
    quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES players (user_id)
);
```

## 🔧 API Endpoints

### Web API
- `GET /` - Home page
- `GET /luckywheel` - Lucky wheel interface
- `GET /api/spin?user_id={id}` - Spin the wheel
- `GET /api/player/{id}` - Get player info
- `POST /webhook` - Telegram webhook endpoint

### Bot API Integration
Web API dipanggil dari Lucky Wheel interface untuk:
- Memproses spin request
- Memberikan random prize berdasarkan rate
- Update player inventory
- Log spin history

## 🛠️ Development

### Adding New Prizes
Edit `LUCKY_WHEEL_PRIZES` di `config.py`:

```python
LUCKY_WHEEL_PRIZES = {
    "new_item": {
        "emoji": "🆕", 
        "name": "New Item",
        "amount": 1,
        "rate": 5  # percentage
    }
}
```

### Customizing Bot Menu
Edit keyboard layout di `bot.py` function `menu()`:

```python
keyboard = [
    [InlineKeyboardButton("BUTTON1", callback_data="action1"),
     InlineKeyboardButton("BUTTON2", callback_data="action2")],
    # Add more rows as needed
]
```

## 🚀 Deployment Options

### Option 1: VPS/Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run with nohup for background process
nohup python run.py > bot.log 2>&1 &

# Or use systemd service for production
```

### Option 2: Cloud Platforms

**Heroku:**
1. Create `Procfile`: `web: python run.py`
2. Set environment variables
3. Deploy via git

**Railway:**
1. Connect GitHub repository
2. Set start command: `python run.py`

**PythonAnywhere:**
1. Upload files
2. Configure virtual environment
3. Run via web interface

### Option 3: Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

## 🔒 Security Notes

- **Token Security**: Never expose BOT_TOKEN in public repositories
- **Database**: SQLite untuk development, consider PostgreSQL untuk production
- **Webhook**: Use HTTPS di production
- **Rate Limiting**: Consider implementing untuk prevent spam
- **Input Validation**: Always validate user inputs

## 📞 Support

Jika ada pertanyaan atau butuh bantuan:

1. Check `config.py` untuk memastikan setting benar
2. Verify bot token dari @BotFather
3. Check database permissions
4. Monitor logs untuk error messages

## 🔄 Updates & Maintenance

### Regular Tasks:
- Backup database file
- Monitor disk space
- Update dependencies
- Check bot logs

### Database Backup:
```bash
cp lootdungeon.db lootdungeon_backup_$(date +%Y%m%d).db
```

---

**Happy Gaming! 🎮🎰**