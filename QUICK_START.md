🚀 **Lucky Wheel Telegram Bot - Quick Start Guide**

========================================================

## 📦 **DOWNLOAD & SETUP**

### 1. **Download File ZIP**
- Download file: `LuckyWheelBot_v1.0.zip`
- Extract ke folder pilihan Anda

### 2. **Edit Konfigurasi (.env)**
Edit file `.env` untuk customisasi:

```env
# Bot Configuration (opsional, sudah diset default)
BOT_TOKEN=8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8
OWNER_ID=6395738130
GROUP_CHAT_ID=-1002917701297
CHANNEL_ID=-1002502508906

# Web Server Configuration
WEB_SERVER_PORT=8081
WEB_SERVER_HOST=0.0.0.0
```

### 3. **Install Dependencies**
```bash
pip install python-telegram-bot==20.7 requests
```

### 4. **Start Bot** (3 Cara)

#### **Cara 1: Quick Start (Recommended)**
```bash
python3 run.py
```

#### **Cara 2: Manual Start**
```bash
# Terminal 1 - Web Server
python3 web_server.py

# Terminal 2 - Bot
python3 bot.py
```

#### **Cara 3: Background Start**
```bash
# Start web server
nohup python3 web_server.py > web_server.log 2>&1 &

# Start bot  
nohup python3 bot.py > bot.log 2>&1 &
```

## 📱 **TESTING BOT**

### **Step 1: Cek Web Server**
- Buka browser: http://localhost:8081/luckywheel.html
- Should melihat Lucky Wheel interface

### **Step 2: Test Bot di Telegram**
1. **Cari bot:** @LuckyWheelRouletteBot
2. **Kirim:** `/start`
3. **Join group & channel** (sesuai instruksi bot)
4. **Kirim:** `/menu`
5. **Test Lucky Wheel:** Klik menu LUCKY WHEEL
6. **Cek Inventory:** Klik menu INVENTORY

## 🛠️ **COMMON COMMANDS**

### **Start Services**
```bash
# Start everything
python3 run.py

# Or individual services
python3 web_server.py    # Web server
python3 bot.py          # Telegram bot
```

### **Stop Services**
```bash
# Kill processes
pkill -f "bot.py"
pkill -f "web_server.py"

# Or use stop script
bash stop.sh
```

### **Check Status**
```bash
# Check if processes are running
ps aux | grep -E "(bot\.py|web_server\.py)"

# Check web server
curl http://localhost:8081

# Check logs
tail -f bot.log
tail -f web_server.log
```

## 🔧 **TROUBLESHOOTING**

### **Port Already in Use**
```bash
# Kill process using port 8081
lsof -ti:8081 | xargs kill -9

# Or use different port
export WEB_SERVER_PORT=8082
python3 web_server.py
```

### **Bot Not Responding**
1. Check token: pastikan BOT_TOKEN benar
2. Check logs: `tail -f bot.log`
3. Restart bot: `python3 bot.py`

### **Mini App Not Loading**
1. Check web server: `curl http://localhost:8081/luckywheel.html`
2. Check port: pastikan WEB_SERVER_PORT=8081
3. Restart web server: `python3 web_server.py`

### **Database Issues**
```bash
# Reset database
rm bot_database.db
python3 bot.py  # Will recreate database
```

## 📊 **FILES STRUCTURE**

```
LuckyWheelBot/
├── bot.py                    # Telegram bot main file
├── web_server.py             # Web server untuk Mini App
├── luckywheel.html           # Mini App interface
├── run.py                   # Main runner script
├── .env                     # Configuration file
├── requirements.txt         # Python dependencies
├── README.md               # Full documentation
├── test_bot.py             # Test suite
├── start.sh                # Startup script
├── stop.sh                 # Stop script
└── QUICK_START.md          # This file
```

## 🎮 **BOT FEATURES**

### **Commands**
- `/start` - Activate bot
- `/menu` - Open game menu

### **Menu 3x3 Grid**
```
[📝 REGISTER] [🎡 LUCKY WHEEL] [🎒 INVENTORY]
[⏳ COMING SOON] [⏳ COMING SOON] [⏳ COMING SOON]
[⏳ COMING SOON] [⏳ COMING SOON] [⏳ COMING SOON]
```

### **8 Lucky Wheel Prizes**
- 💰 1x = 100 Fizz Coin
- 💰 3x = 300 Fizz Coin
- 💰 5x = 500 Fizz Coin
- 🎫 1x = 1 Lucky Ticket
- 🎫 3x = 3 Lucky Ticket
- 🎫 5x = 5 Lucky Ticket
- 🧪 5x = 5 HP Potion
- ☠️ = Zonk

### **Registration Flow**
1. User sends `/start`
2. Bot directs to join group & channel
3. User clicks REGISTER to verify
4. After verified → access all features

## 🏆 **OWNER FEATURES**

Owner (ID: 6395738130) gets:
- ✅ **Unlimited Lucky Tickets**
- ✅ **All privileges**
- ✅ **Owner badge** in Mini App

## 📞 **SUPPORT**

If you encounter issues:
1. Check logs: `tail -f bot.log web_server.log`
2. Test with: `python3 test_bot.py`
3. Restart services
4. Check configuration in `.env`

---

**🎉 Enjoy your Lucky Wheel Bot!** 🎡

Need help? Check README.md for full documentation.