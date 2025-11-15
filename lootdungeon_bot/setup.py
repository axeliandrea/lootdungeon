"""
Deployment script untuk LootDungeon Bot
Jalankan script ini untuk setup environment
"""
import os
import subprocess
import sys

def install_requirements():
    """Install dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    print("✅ Directories created!")

def check_config():
    """Check if config file is properly set"""
    print("⚙️ Checking configuration...")
    try:
        from config import BOT_TOKEN, OWNER_ID
        if BOT_TOKEN == "8533524958:AAEgMfl3NS9SzTMCOpy1YpJMGQfNzKcdvv8":
            print("✅ Configuration loaded successfully!")
            return True
        else:
            print("⚠️ BOT_TOKEN not found or invalid in config.py")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def initialize_database():
    """Initialize database"""
    print("🗄️ Initializing database...")
    try:
        from database import Database
        db = Database()
        print("✅ Database initialized!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LootDungeon Bot Setup")
    print("=" * 40)
    
    # Check if running in correct directory
    if not os.path.exists("config.py"):
        print("❌ Please run this script from the lootdungeon_bot directory")
        return False
    
    # Run setup steps
    steps = [
        ("Installing Dependencies", install_requirements),
        ("Setting Up Directories", setup_directories),
        ("Checking Configuration", check_config),
        ("Initializing Database", initialize_database)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            return False
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config.py with your domain")
    print("2. Run: python run.py")
    print("3. Access bot on Telegram")
    print("4. Visit: http://yourdomain.com")
    
    return True

if __name__ == "__main__":
    main()