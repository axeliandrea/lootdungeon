"# 🤖 Telegram Bot Guide - @dhloot_bot

Panduan lengkap penggunaan Telegram Bot untuk Lucky Wheel Roulette.

## 📋 Table of Contents
- [Setup Bot](#setup-bot)
- [Commands](#commands)
- [Features](#features)
- [Anti-Spam Protection](#anti-spam-protection)
- [Troubleshooting](#troubleshooting)

## 🔧 Setup Bot

### 1. Membuat Telegram Bot

1. Buka Telegram dan chat [@BotFather](https://t.me/BotFather)
2. Kirim command `/newbot`
3. Ikuti instruksi:
   ```
   - Masukkan nama bot: Lucky Wheel Bot
   - Masukkan username: dhloot_bot (harus unik dan diakhiri 'bot')
   ```
4. BotFather akan memberikan **Bot Token**:
   ```
   8522624352:AAGAPF_Jrsbqy7PsRnAAgGH4ZFN0g_kyHc0
   ```
5. **JANGAN SHARE token ini ke siapapun!**

### 2. Mendapatkan Group Chat ID

1. Invite bot Anda ke group Telegram
2. Invite [@RawDataBot](https://t.me/RawDataBot) ke group
3. RawDataBot akan mengirim info group, copy nilai `chat.id`:
   ```json
   {
     \"chat\": {
       \"id\": -1002917701297,
       \"title\": \"Lucky Wheel Group\"
     }
   }
   ```
4. Group ID selalu **negative number** untuk group

### 3. Mendapatkan Owner ID

1. Chat [@userinfobot](https://t.me/userinfobot)
2. Bot akan reply dengan info Anda:
   ```
   Id: 6395738130
   First name: Your Name
   Username: @yourusername
   ```
3. Copy nilai `Id`

### 4. Configure Bot di Backend

Edit file `backend/.env`:
```env
TELEGRAM_BOT_TOKEN=\"8522624352:AAGAPF_Jrsbqy7PsRnAAgGH4ZFN0g_kyHc0\"
TELEGRAM_GROUP_ID=\"-1002917701297\"
OWNER_ID=\"6395738130\"
```

## 🎮 Commands

### User Commands (Semua Orang)

#### `/start`
**Fungsi**: Registrasi user baru ke sistem

**Usage**:
```
/start
```

**Response**:
```
🎰 Welcome to Lucky Wheel Roulette! 🎰

👋 Hi [Name]!

Commands:
🎟️ /mytickets - Check your tickets & points
💰 /buyticket [amount] - Buy tickets with points (25 points = 1 ticket)

How to get tickets:
• Claim from group giveaways
• Earn points by chatting in group (5 characters = 1 point)
• Buy with points

🌐 Play now: Visit the web app to spin the wheel!
```

---

#### `/mytickets`
**Fungsi**: Cek status tiket dan points Anda

**Usage**:
```
/mytickets
```

**Response**:
```
🎟️ Your Stats

👤 User: John
🎫 Tickets: 5
⭐ Points: 150
🎰 Total Spins: 12

💡 25 points = 1 ticket
```

---

#### `/buyticket [amount]`
**Fungsi**: Beli tiket menggunakan points

**Usage**:
```
/buyticket 2
```

**Requirements**:
- 1 ticket = 25 points
- Minimum 1 ticket
- Harus punya cukup points

**Success Response**:
```
✅ Purchase Successful!

🎟️ Tickets bought: 2
💰 Points spent: 50

New Balance:
🎫 Tickets: 7
⭐ Points: 100
```

**Error Response**:
```
❌ Not enough points!

You have: 20 points
You need: 50 points

💡 Keep chatting in the group to earn points!
(5 characters = 1 point)
```

### Owner Commands (Khusus Owner)

#### `/giveticket [amount]`
**Fungsi**: Bagikan tiket ke group dengan inline button CLAIM

**Usage**:
```
/giveticket 5
```

**Requirements**:
- Hanya owner yang bisa gunakan
- Harus digunakan di group (bukan PM)
- Amount: 1-10 tiket

**Response**:
```
🎁 TICKET GIVEAWAY! 🎁

🎟️ Tickets: 5
⏰ Expires in: 1 minute

👇 Click the button below to claim!

[ 🎟️ CLAIM TICKET ]
```

**Inline Button Behavior**:
- Setiap user hanya bisa claim 1x
- Button expire dalam 1 menit
- Anti-spam protection
- Notifikasi di chat saat ada yang claim

**After Expiry**:
```
🎁 TICKET GIVEAWAY! 🎁

🎟️ Tickets: 5
❌ EXPIRED
```

## ✨ Features

### 1. Point System

**Cara Mendapat Points**:
- Kirim pesan di group
- 5 karakter = 1 point
- Otomatis dihitung oleh bot

**Contoh**:
```
User: \"Hello\" (5 chars) → +1 point
User: \"Hello World!\" (12 chars) → +2 points
User: \"Hi\" (2 chars) → +0 points (minimal 5)
```

**Menggunakan Points**:
- Buy tickets: 25 points = 1 ticket
- `/buyticket [amount]`

### 2. Ticket Claim System

**Flow**:
1. Owner `/giveticket 5` di group
2. Bot post message dengan inline button
3. User klik button \"CLAIM TICKET\"
4. Bot cek:
   - Apakah sudah expired? (1 menit)
   - Apakah user sudah claim?
   - Jika valid → berikan tiket
5. Notifikasi ke group: \"🎉 @username claimed 5 ticket(s)!\"

**Anti-Spam Features**:
- ✅ Double-claim prevention (1 user = 1 claim per giveaway)
- ✅ Time-based expiry (1 minute)
- ✅ Database lock untuk race condition
- ✅ Callback validation

### 3. Spin Notification

**Automatic Notification ke Group**:

Setiap kali user spin wheel di web app, bot otomatis post ke group:

```
🎰 LUCKY WHEEL RESULT! 🎰

🎁 Prize: Jackpot 1000
👤 Winner: @username
🎟️ Tickets left: 4
```

## 🔒 Anti-Spam Protection

### Double Claim Prevention

**Database Check**:
```python
if user.id in ticket_claim.get('claimed_by', []):
    await query.answer(\"You already claimed this!\", show_alert=True)
    return
```

**Result**: User tidak bisa claim tiket yang sama 2x

### Time-Based Expiry

**Implementation**:
```python
expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
```

**Result**: 
- Button hanya valid 1 menit
- Setelah 1 menit, claim akan ditolak
- Button text berubah menjadi \"EXPIRED\"

### Rate Limiting (Built-in)

Telegram Bot API memiliki rate limit:
- 30 messages per second
- 20 messages per minute per group

## 🧪 Testing Bot

### Test Locally

1. **Start Bot**:
   ```bash
   cd backend
   python server.py
   ```

2. **Test Commands**:
   ```
   # Test di private chat
   /start
   /mytickets
   /buyticket 1

   # Test di group (as owner)
   /giveticket 3
   ```

3. **Test Claim**:
   - Klik inline button \"CLAIM TICKET\"
   - Verify user dapat tiket
   - Try claim lagi (harus error)

4. **Test Point Earning**:
   - Chat di group: \"Hello world this is a test message\"
   - `/mytickets` → cek points bertambah

5. **Test Spin**:
   - Login ke web app
   - Spin wheel
   - Cek notification di group

### Test Production

1. **Verify Bot Online**:
   ```bash
   curl \"https://api.telegram.org/bot<TOKEN>/getMe\"
   ```

2. **Check Webhook Status**:
   ```bash
   curl \"https://api.telegram.org/bot<TOKEN>/getWebhookInfo\"
   ```

   Result harus: `\"url\": \"\"` (webhook disabled, using polling)

## 🐛 Troubleshooting

### Bot Tidak Merespon

**Possible Causes**:
1. Backend tidak jalan
2. Bot token salah
3. Network issue

**Solution**:
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Verify bot token
curl \"https://api.telegram.org/bot<TOKEN>/getMe\"

# Restart backend
sudo supervisorctl restart backend
```

### Command `/giveticket` Tidak Jalan

**Error**: \"Only the owner can use this command!\"

**Solution**:
- Pastikan `OWNER_ID` di `.env` sesuai dengan Telegram ID Anda
- Restart backend setelah update env

**Error**: \"This command can only be used in the group!\"

**Solution**:
- Gunakan command di group, bukan private chat
- Pastikan bot sudah di-invite ke group

### Inline Button Tidak Berfungsi

**Error**: \"This giveaway has expired!\"

**Solution**:
- Button memang expired setelah 1 menit
- Request owner untuk `/giveticket` lagi

**Error**: \"You already claimed this!\"

**Solution**:
- Anti-spam protection bekerja
- 1 user hanya bisa claim 1x per giveaway

### Point Tidak Bertambah

**Possible Causes**:
1. Chat bukan di group yang benar
2. Message terlalu pendek (<5 karakter)
3. Bot tidak tracking

**Solution**:
```bash
# Verify TELEGRAM_GROUP_ID correct
echo $TELEGRAM_GROUP_ID

# Check bot logs
tail -f /var/log/supervisor/backend.out.log | grep \"points_earned\"
```

### Notification Tidak Muncul di Group

**Possible Causes**:
1. Group ID salah
2. Bot tidak di-invite ke group
3. Bot tidak admin (optional, tapi recommended)

**Solution**:
1. Verify group ID dengan RawDataBot
2. Invite bot ke group
3. Make bot admin (Settings → Administrators)

## 📊 Bot Analytics

### Check User Stats

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['lucky_wheel_db']

# Total users
total_users = db.users.count_documents({})

# Total tickets distributed
total_tickets = db.users.aggregate([
    {\"$group\": {\"_id\": None, \"total\": {\"$sum\": \"$tickets\"}}}
])

# Total spins
total_spins = db.spin_history.count_documents({})

print(f\"Total Users: {total_users}\")
print(f\"Total Tickets: {total_tickets}\")
print(f\"Total Spins: {total_spins}\")
```

## 🔐 Security Best Practices

1. **Bot Token**:
   - Never share publicly
   - Use environment variables
   - Different tokens for dev/prod

2. **Owner Verification**:
   - Always verify owner ID before admin commands
   - Don't hardcode owner ID in code

3. **Rate Limiting**:
   - Implement custom rate limiting for spam prevention
   - Monitor bot usage

4. **Data Validation**:
   - Validate all user inputs
   - Sanitize database queries
   - Check expiry before processing

## 📞 Support

**Bot Issues**:
- Check logs: `/var/log/supervisor/backend.err.log`
- Restart bot: `sudo supervisorctl restart backend`
- Verify credentials in `.env`

**Feature Requests**:
- Create issue di GitHub
- DM owner di Telegram

---

**Enjoy the Lucky Wheel! 🎰✨**
"
