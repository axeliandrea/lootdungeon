"# 🎰 Lucky Wheel Roulette

Aplikasi Lucky Wheel Roulette dengan integrasi Telegram Bot untuk pembagian tiket dan notifikasi hasil spin.

## ✨ Fitur Utama

### Web Application
- 🎡 Roulette wheel interaktif dengan 10 hadiah
- 🎨 UI modern dengan glassmorphism dan animasi smooth
- 🎊 Efek confetti saat menang
- 📊 Dashboard untuk melihat tiket, points, dan history
- 🔐 Login menggunakan Telegram ID

### Telegram Bot (@dhloot_bot)
- 📨 **Command `/start`** - Registrasi user baru
- 🎫 **Command `/mytickets`** - Cek tiket & points
- 🎁 **Command `/giveticket [jumlah]`** - Owner bagikan tiket (expired 1 menit)
- 💰 **Command `/buyticket [jumlah]`** - Beli tiket dengan points (25 points = 1 tiket)
- 💬 **Point System** - Earn points dengan chatting di group (5 karakter = 1 point)
- ✅ **Inline Button CLAIM** - Klaim tiket dengan anti-spam protection
- 📢 **Auto Notification** - Hasil spin otomatis di-post ke group

## 🎁 10 Hadiah

1. Gold 100
2. Silver 50
3. Bronze 25
4. Jackpot 1000
5. Diamond
6. Ruby
7. Emerald
8. Sapphire
9. Pearl
10. Lucky Star

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js + Tailwind CSS + Shadcn UI
- **Database**: MongoDB
- **Telegram Bot**: python-telegram-bot v21.0

## 📋 Prerequisites

- Python 3.11+
- Node.js 16+
- MongoDB
- Telegram Bot Token

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/axeliandrea/ATA.git
cd ATA
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file dengan konfigurasi Anda:
# MONGO_URL=\"mongodb://localhost:27017\"
# DB_NAME=\"lucky_wheel_db\"
# TELEGRAM_BOT_TOKEN=\"your_bot_token\"
# TELEGRAM_GROUP_ID=\"your_group_chat_id\"
# OWNER_ID=\"your_telegram_user_id\"

# Run backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
yarn install

# Configure environment variables
# Create .env file:
# REACT_APP_BACKEND_URL=http://localhost:8001

# Run frontend
yarn start
```

## 🔧 Konfigurasi Telegram Bot

### Mendapatkan Bot Token
1. Chat [@BotFather](https://t.me/BotFather) di Telegram
2. Ketik `/newbot` dan ikuti instruksi
3. Copy Bot Token yang diberikan
4. Masukkan ke `.env` sebagai `TELEGRAM_BOT_TOKEN`

### Mendapatkan Group Chat ID
1. Invite bot Anda ke group
2. Invite [@RawDataBot](https://t.me/RawDataBot) ke group
3. Copy `chat.id` yang muncul
4. Masukkan ke `.env` sebagai `TELEGRAM_GROUP_ID`

### Mendapatkan Owner ID
1. Chat [@userinfobot](https://t.me/userinfobot)
2. Copy `Id` yang muncul
3. Masukkan ke `.env` sebagai `OWNER_ID`

## 📖 Cara Penggunaan

### Untuk Owner

1. **Bagikan Tiket ke Group**
   ```
   /giveticket 5
   ```
   - Akan muncul inline button \"CLAIM TICKET\"
   - Button expired dalam 1 menit
   - Setiap user hanya bisa claim 1x per giveaway

2. **Cek Status User**
   ```
   /mytickets
   ```

### Untuk User

1. **Mulai Bot**
   ```
   /start
   ```
   - Registrasi ke database
   - Dapatkan instruksi penggunaan

2. **Claim Tiket**
   - Klik button \"CLAIM TICKET\" di group
   - Tidak bisa double claim
   - Expired dalam 1 menit

3. **Earn Points**
   - Chat di group untuk mendapatkan points
   - 5 karakter = 1 point
   - Points bisa digunakan untuk beli tiket

4. **Beli Tiket dengan Points**
   ```
   /buyticket 2
   ```
   - 25 points = 1 ticket
   - Points otomatis terpotong

5. **Spin the Wheel**
   - Buka web app: http://localhost:3000
   - Login dengan Telegram ID
   - Klik \"SPIN THE WHEEL!\"
   - Hasil otomatis di-post ke group

## 🔐 Security Features

- ✅ Anti-spam protection untuk claim button
- ✅ Owner-only command untuk `/giveticket`
- ✅ Ticket expiry system (1 menit)
- ✅ Validasi user dan ticket sebelum spin
- ✅ Database lock untuk prevent race condition

## 📁 Project Structure

```
ATA/
├── backend/
│   ├── server.py           # Main FastAPI app + Telegram bot
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── components/
│   │       └── LuckyWheel.jsx
│   ├── package.json
│   └── .env
└── README.md
```

## 🎮 API Endpoints

- `GET /api/` - Health check
- `GET /api/user/{telegram_id}` - Get user info
- `POST /api/spin` - Spin the wheel
- `GET /api/history/{telegram_id}` - Get spin history
- `GET /api/prizes` - Get list of prizes

## 🐛 Troubleshooting

### Bot tidak merespon
- Pastikan `TELEGRAM_BOT_TOKEN` benar
- Cek backend logs untuk error
- Restart backend service

### Hasil spin tidak muncul di group
- Pastikan `TELEGRAM_GROUP_ID` benar (harus negative number untuk group)
- Pastikan bot adalah admin di group

### User tidak bisa login
- User harus `/start` bot terlebih dahulu
- Telegram ID harus valid

## 📝 Environment Variables

### Backend (.env)
```
MONGO_URL=\"mongodb://localhost:27017\"
DB_NAME=\"lucky_wheel_db\"
CORS_ORIGINS=\"*\"
TELEGRAM_BOT_TOKEN=\"your_bot_token_here\"
TELEGRAM_GROUP_ID=\"-1002917701297\"
OWNER_ID=\"6395738130\"
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🚀 Deployment to GitHub

### 1. Initialize Git (if not already)
```bash
git init
```

### 2. Add Remote Repository
```bash
git remote add origin https://github.com/axeliandrea/ATA.git
```

### 3. Add and Commit Files
```bash
git add .
git commit -m \"Initial commit: Lucky Wheel Roulette with Telegram Bot integration\"
```

### 4. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

### 5. IMPORTANT: Secure Your Credentials
Before pushing, make sure to:
- Never commit `.env` files to GitHub
- Add `.env` to `.gitignore`
- Use environment variables for production
- Update bot token and group ID in production environment

## 📄 License

MIT License

## 👨‍💻 Author

Created with ❤️ by Emergent AI

---

**Happy Spinning! 🎰✨**
"
