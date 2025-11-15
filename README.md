# 🎡 Lucky Wheel Telegram Bot dengan Mini App

Bot Telegram yang menampilkan Lucky Wheel Roulette menggunakan Mini App dengan sistem inventory dan database sinkronisasi.

## 📋 Fitur

### 🎮 Game Features
- **Lucky Wheel Roulette** dengan animasi yang menarik
- **8 Jenis Hadiah** dengan probabilitas yang seimbang
- **Sistem Inventory** untuk menyimpan semua hadiah
- **Verifikasi Membership** - player harus join group dan channel
- **Owner Mode** - owner mendapat tiket unlimited

### 💎 Hadiah yang Tersedia
- 💰 **1x** = 100 Fizz Coin
- 💰 **3x** = 300 Fizz Coin  
- 💰 **5x** = 500 Fizz Coin
- 🎫 **1x** = 1 Lucky Ticket
- 🎫 **3x** = 3 Lucky Ticket
- 🎫 **5x** = 5 Lucky Ticket
- 🧪 **5x** = 5 HP Potion
- ☠️ = Zonk (手氣不順)

### 🛠️ Menu 3x3 Grid
```
[REGISTER]    [LUCKY WHEEL]    [INVENTORY]
[COMING SOON] [COMING SOON]   [COMING SOON]
[COMING SOON] [COMING SOON]   [COMING SOON]
```

## 🚀 Instalasi

### Persyaratan
- Python 3.7+
- pip3
- Internet connection

### Langkah Instalasi

1. **Jalankan script setup:**
```bash
chmod +x /workspace/setup.sh
bash /workspace/setup.sh
```

2. **Atau instalasi manual:**
```bash
pip3 install python-telegram-bot==20.7 requests
```

## 🎯 Penggunaan

### Menjalankan Bot

```bash
python3 /workspace/run.py
```

Script ini akan otomatis:
1. ✅ Memulai web server di port 8080
2. ✅ Menjalankan Telegram bot
3. ✅ Setup database SQLite
4. ✅ Menyediakan Mini App

### Command Telegram

- `/start` - Aktivasi bot dan tampilkan informasi
- `/menu` - Buka menu game dengan keyboard inline

### Flow Registrasi

1. **Player** mengetik `/start`
2. **Arahkan** player join Group Chat: https://t.me/your_group
3. **Arahkan** player join Channel: https://t.me/your_channel
4. **Klik** menu REGISTER untuk verifikasi membership
5. **Berhasil** jika sudah join group dan channel
6. **Akses** semua fitur setelah registrasi berhasil

### Menggunakan Lucky Wheel

1. Klik menu **LUCKY WHEEL**
2. **otomatis** berkurang 1 ticket (kecuali owner)
3. Buka **Mini App** dengan animasi roulette
4. Spin dan lihat hasil
5. Hadiah **otomatis** masuk ke inventory

### Cek Inventory

1. Klik menu **INVENTORY**
2. Lihat **sub menu**: LIHAT SEMUA ITEM dan GUNAKAN HP POTION
3. Inventory menampilkan: Fizz Coin, Lucky Ticket, HP Potion

## 🏗️ Arsitektur

### Komponen Utama

1. **bot.py** - Telegram bot handler
   - Command processing
   - Menu keyboard
   - Membership verification
   - Database operations

2. **web_server.py** - Web server untuk Mini App
   - Host Lucky Wheel HTML
   - API endpoint untuk hasil spin
   - CORS handling

3. **luckywheel.html** - Mini App interface
   - Interactive wheel animation
   - Prize selection logic
   - Telegram Web App integration

4. **Database SQLite** - Data persistence
   - User profiles
   - Inventory management
   - Spin history

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    registered BOOLEAN DEFAULT FALSE,
    join_group BOOLEAN DEFAULT FALSE,
    join_channel BOOLEAN DEFAULT FALSE,
    fizz_coin INTEGER DEFAULT 0,
    lucky_ticket INTEGER DEFAULT 3,
    hp_potion INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_spin TIMESTAMP
);

-- Spin history
CREATE TABLE spin_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    prize_type TEXT,
    prize_value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Prizes configuration
CREATE TABLE prizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prize_type TEXT,
    prize_value INTEGER,
    prize_name TEXT,
    emoji TEXT
);
```

## ⚙️ Konfigurasi

### Variables dalam bot.py

```python
BOT_TOKEN = "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8"
OWNER_ID = 6395738130
GROUP_CHAT_ID = -1002917701297
CHANNEL_ID = -1002502508906
WEB_SERVER_URL = "http://localhost:8080"
```

### Customization

#### Mengubah Hadiah
Edit array `prizes` dalam `luckywheel.html`:

```javascript
const prizes = [
    { type: 'fizz_coin', value: 100, emoji: '💰 1x', color: '#ff6b6b' },
    // ... tambah/edit hadiah
];
```

#### Mengubah Probabilitas
Edit fungsi `spinWheel()` untuk mengatur probabilitas:

```javascript
const weights = [10, 5, 2, 15, 8, 3, 5, 52]; // Probabilitas setiap hadiah
```

#### Mengubah Port Web Server
```python
# Di web_server.py
port = int(os.environ.get('MINI_APP_PORT', 8080))
```

## 🐛 Troubleshooting

### Bot Tidak Merespon
1. Periksa token bot valid
2. Pastikan bot sudah di-start di Telegram
3. Cek koneksi internet
4. Lihat log error

### Mini App Tidak Terbuka
1. Pastikan web server running di port 8080
2. Cek firewall tidak blocking port 8080
3. Pastikan URL web server correct

### Database Error
1. Hapus file `bot_database.db`
2. Restart bot untuk regenerate database
3. Periksa permissions file

### Error Dependency
```bash
pip3 install --upgrade python-telegram-bot requests
```

## 📊 Monitoring

### Log Files
- Console output akan menampilkan semua aktivitas
- Error dan info akan logged dengan timestamp

### Database Access
```bash
sqlite3 bot_database.db
.tables
SELECT * FROM users;
SELECT * FROM spin_history;
```

## 🔧 Development

### Struktur File
```
/workspace/
├── bot.py              # Telegram bot main file
├── web_server.py       # Web server untuk Mini App
├── luckywheel.html     # Mini App interface
├── run.py             # Main runner script
├── setup.sh           # Setup script
├── requirements.txt   # Python dependencies
└── README.md          # Dokumentasi
```

### Adding New Features

1. **Tambah Menu**: Edit keyboard di fungsi `menu()`
2. **Tambah Command**: Tambah handler di `main()`
3. **Tambah Database Field**: Update `DatabaseManager.init_database()`
4. **Custom Hadiah**: Edit array `prizes` di `luckywheel.html`

## 🛡️ Security

- Token bot dijaga aman dalam environment
- Database SQLite local, tidak exposure ke internet
- Input validation untuk semua user input
- Rate limiting bisa ditambahkan untuk mencegah spam

## 📈 Future Enhancements

- [ ] RPG character system
- [ ] Shop system untuk beli tiket
- [ ] Leaderboard
- [ ] Daily bonus system
- [ ] Event system
- [ ] Admin panel
- [ ] Webhook deployment

## 📞 Support

Jika ada masalah atau pertanyaan:
1. Cek dokumentasi ini
2. Lihat log error
3. Pastikan semua dependencies terinstall
4. Restart semua proses

---

**Dibuat dengan ❤️ untuk Lucky Wheel Gaming Bot**