"# 🚀 Deployment Guide - Lucky Wheel Roulette

Panduan lengkap untuk deploy aplikasi Lucky Wheel Roulette ke GitHub dan berbagai platform hosting.

## 📦 Persiapan Sebelum Deploy

### 1. Security Checklist
- ✅ Pastikan file `.env` sudah di-exclude di `.gitignore`
- ✅ Buat file `.env.example` sebagai template (sudah tersedia)
- ✅ Jangan commit sensitive credentials ke repository
- ✅ Gunakan environment variables untuk production

### 2. File yang Harus Ada
```
ATA/
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── server.py
└── frontend/
    ├── .env.example
    ├── package.json
    └── src/
```

## 🔧 Push ke GitHub

### Step 1: Initialize Git Repository
```bash
cd /path/to/ATA
git init
```

### Step 2: Add Remote Origin
```bash
git remote add origin https://github.com/axeliandrea/ATA.git
```

### Step 3: Add Files
```bash
# Add all files (gitignore akan exclude .env otomatis)
git add .

# Check status
git status

# Pastikan .env tidak masuk dalam staging
```

### Step 4: Commit Changes
```bash
git commit -m \"feat: Lucky Wheel Roulette with Telegram Bot integration

Features:
- Interactive roulette wheel with 10 prizes
- Telegram bot integration for ticket distribution
- Point system (5 chars = 1 point)
- Ticket claim with inline button (1 min expiry)
- Anti-spam protection
- Auto notification to Telegram group
- User dashboard with history
- Beautiful glassmorphism UI\"
```

### Step 5: Push to GitHub
```bash
# Create main branch
git branch -M main

# Push to remote
git push -u origin main
```

### Step 6: Verify
1. Buka https://github.com/axeliandrea/ATA
2. Pastikan file `.env` **TIDAK** ada di repository
3. Pastikan `.env.example` ada
4. Check README.md tampil dengan baik

## 🌐 Deploy ke Platform Hosting

### Option 1: Deploy ke Railway.app

Railway sangat mudah untuk deploy full-stack app dengan MongoDB.

#### Step 1: Setup Railway
1. Daftar di [Railway.app](https://railway.app)
2. Connect GitHub account
3. Click \"New Project\" → \"Deploy from GitHub repo\"
4. Pilih repository `ATA`

#### Step 2: Configure Services
Railway akan auto-detect FastAPI dan React. Anda perlu:

1. **Add MongoDB Service**
   - Click \"New\" → \"Database\" → \"MongoDB\"
   - Copy MongoDB connection URL

2. **Configure Backend Service**
   - Select backend directory
   - Add environment variables:
     ```
     MONGO_URL=<railway_mongodb_url>
     DB_NAME=lucky_wheel_db
     TELEGRAM_BOT_TOKEN=8522624352:AAGAPF_Jrsbqy7PsRnAAgGH4ZFN0g_kyHc0
     TELEGRAM_GROUP_ID=-1002917701297
     OWNER_ID=6395738130
     CORS_ORIGINS=*
     ```
   - Set start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

3. **Configure Frontend Service**
   - Select frontend directory
   - Add environment variable:
     ```
     REACT_APP_BACKEND_URL=<backend_railway_url>
     ```
   - Railway akan auto-detect React dan build

#### Step 3: Deploy
- Click \"Deploy\"
- Railway akan build dan deploy otomatis
- Dapatkan URL untuk frontend dan backend

### Option 2: Deploy ke Render.com

Render bagus untuk free tier dengan auto-deploy dari GitHub.

#### Step 1: Create Web Services
1. Sign up di [Render.com](https://render.com)
2. Connect GitHub repository

#### Step 2: Create Backend Service
1. New → Web Service
2. Connect `ATA` repository
3. Settings:
   - **Name**: lucky-wheel-backend
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables (sama seperti Railway)
5. Create Web Service

#### Step 3: Create Frontend Service
1. New → Static Site
2. Connect `ATA` repository
3. Settings:
   - **Name**: lucky-wheel-frontend
   - **Root Directory**: frontend
   - **Build Command**: `yarn install && yarn build`
   - **Publish Directory**: build
4. Add Environment Variable:
   ```
   REACT_APP_BACKEND_URL=<backend_render_url>
   ```
5. Create Static Site

#### Step 4: MongoDB
1. New → PostgreSQL (atau gunakan MongoDB Atlas external)
2. Atau gunakan [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier 512MB)

### Option 3: Deploy ke VPS (DigitalOcean, AWS EC2, dll)

#### Requirements
- Ubuntu 22.04 LTS
- 2GB RAM minimum
- Domain (optional)

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nodejs npm mongodb nginx

# Install yarn
npm install -g yarn

# Install PM2 for process management
npm install -g pm2
```

#### Step 2: Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/axeliandrea/ATA.git
cd ATA
```

#### Step 3: Setup Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Paste your actual env variables

# Start with PM2
pm2 start \"uvicorn server:app --host 0.0.0.0 --port 8001\" --name lucky-wheel-backend
pm2 save
pm2 startup
```

#### Step 4: Setup Frontend
```bash
cd ../frontend

# Install dependencies
yarn install

# Create .env file
sudo nano .env
# Add: REACT_APP_BACKEND_URL=http://your-domain.com/api

# Build
yarn build

# Serve with nginx (configure below)
```

#### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/lucky-wheel
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/ATA/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lucky-wheel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 6: Setup SSL (Optional but Recommended)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔄 Auto-Deploy dengan GitHub Actions

Buat file `.github/workflows/deploy.yml`:

```yaml
name: Deploy Lucky Wheel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Railway
      run: |
        # Railway CLI commands
        # Install: npm install -g @railway/cli
        railway up
```

## 📱 Testing Deployment

### Backend Health Check
```bash
curl https://your-backend-url.com/api/
```

Expected response:
```json
{\"message\":\"Lucky Wheel Roulette API\"}
```

### Frontend Access
1. Buka browser: https://your-frontend-url.com
2. Test login dengan Telegram ID
3. Test spin functionality

### Telegram Bot Test
1. Chat bot: `/start`
2. Group command: `/giveticket 1`
3. Click CLAIM button
4. Spin wheel di web app
5. Cek notifikasi di group

## 🐛 Common Issues

### Bot Tidak Jalan di Production
- Pastikan webhook tidak aktif (bot menggunakan polling)
- Check firewall tidak block Telegram API
- Verify bot token di environment variables

### CORS Error
- Tambahkan domain frontend ke `CORS_ORIGINS`
- Format: `CORS_ORIGINS=https://frontend.com,https://www.frontend.com`

### MongoDB Connection Failed
- Pastikan MongoDB URL correct
- Whitelist IP di MongoDB Atlas (jika pakai Atlas)
- Check network security group

### Environment Variables Tidak Terbaca
- Restart service setelah update env vars
- Verify env vars dengan: `echo $VARIABLE_NAME`
- Platform hosting: check dashboard environment section

## 📊 Monitoring

### Logs Railway
```bash
railway logs
```

### Logs Render
Check di dashboard → Logs tab

### Logs VPS
```bash
# Backend logs
pm2 logs lucky-wheel-backend

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 🔐 Security Best Practices

1. **Never commit .env files**
2. **Use different bot tokens for dev and production**
3. **Enable rate limiting** di API
4. **Setup firewall** di VPS
5. **Regular backups** untuk MongoDB
6. **Use HTTPS** untuk production
7. **Monitor logs** untuk suspicious activity

## 📞 Support

Jika ada masalah deployment:
1. Check logs untuk error messages
2. Verify environment variables
3. Test locally first
4. Create issue di GitHub repository

---

**Happy Deploying! 🚀**
"
