import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PrizeType(Enum):
    """Tipe hadiah dalam lucky wheel"""
    FIZZ_COIN = "fizz_coin"
    TICKET = "ticket"
    HP_POTION = "hp_potion"
    MP_POTION = "mp_potion"
    JACKPOT = "jackpot"

@dataclass
class LuckyWheelPrize:
    """Struktur data untuk hadiah lucky wheel"""
    name: str
    prize_type: PrizeType
    value: int
    chance_percentage: float
    description: str
    icon: str = "🎰"

class LuckyWheelManager:
    """Manajemen sistem lucky wheel"""
    
    def __init__(self, data_file: str = "lucky_wheel_data.json"):
        self.data_file = data_file
        self.prizes = self._initialize_prizes()
        self.user_data = self._load_user_data()
    
    def _initialize_prizes(self) -> List[LuckyWheelPrize]:
        """Inisialisasi daftar hadiah lucky wheel"""
        return [
            # Hadiah Fizz Coin
            LuckyWheelPrize("Fizz Coin 10", PrizeType.FIZZ_COIN, 10, 25.0, "Mendapatkan 10 Fizz Coin", "💰"),
            LuckyWheelPrize("Fizz Coin 50", PrizeType.FIZZ_COIN, 50, 15.0, "Mendapatkan 50 Fizz Coin", "💰"),
            LuckyWheelPrize("Fizz Coin 100", PrizeType.FIZZ_COIN, 100, 8.0, "Mendapatkan 100 Fizz Coin", "💰"),
            
            # Hadiah Tiket Lucky Wheel
            LuckyWheelPrize("Tiket Lucky Wheel 3x", PrizeType.TICKET, 3, 20.0, "Mendapatkan 3 tiket lucky wheel", "🎫"),
            LuckyWheelPrize("Tiket Lucky Wheel 10x", PrizeType.TICKET, 10, 5.0, "Mendapatkan 10 tiket lucky wheel", "🎫"),
            
            # Hadiah Potion
            LuckyWheelPrize("Potion HP (+50)", PrizeType.HP_POTION, 50, 15.0, "Menambahkan 50 HP", "🧪"),
            LuckyWheelPrize("Potion MP (+20)", PrizeType.MP_POTION, 20, 10.0, "Menambahkan 20 MP", "🧪"),
            
            # Jackpot
            LuckyWheelPrize("JACKPOT Fizz Coin 5000", PrizeType.JACKPOT, 5000, 2.0, "JACKPOT! 5000 Fizz Coin", "🎉"),
        ]
    
    def _load_user_data(self) -> Dict:
        """Memuat data pengguna dari file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_user_data(self):
        """Menyimpan data pengguna ke file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silent fail untuk file I/O errors
    
    def _get_user_tickets(self, user_id: int) -> int:
        """Mendapatkan jumlah tiket user"""
        return self.user_data.get(str(user_id), {}).get('tickets', 0)
    
    def _set_user_tickets(self, user_id: int, tickets: int):
        """Mengatur jumlah tiket user"""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {}
        self.user_data[str(user_id)]['tickets'] = tickets
        self._save_user_data()
    
    def _add_user_tickets(self, user_id: int, amount: int):
        """Menambah tiket user"""
        current_tickets = self._get_user_tickets(user_id)
        self._set_user_tickets(user_id, current_tickets + amount)
    
    def _get_user_cooldowns(self, user_id: int) -> Dict[str, datetime]:
        """Mendapatkan cooldown user"""
        return self.user_data.get(str(user_id), {}).get('cooldowns', {})
    
    def _set_user_cooldown(self, user_id: int, action: str, cooldown_duration: timedelta):
        """Mengatur cooldown untuk user"""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {}
        if 'cooldowns' not in self.user_data[str(user_id)]:
            self.user_data[str(user_id)]['cooldowns'] = {}
        
        self.user_data[str(user_id)]['cooldowns'][action] = datetime.now() + cooldown_duration
        self._save_user_data()
    
    def _check_cooldown(self, user_id: int, action: str) -> bool:
        """Memeriksa apakah user masih dalam cooldown"""
        cooldowns = self._get_user_cooldowns(user_id)
        if action not in cooldowns:
            return True
        
        cooldown_end = cooldowns[action]
        if datetime.now() > cooldown_end:
            return True
        
        remaining_time = cooldown_end - datetime.now()
        return False
    
    def get_user_tickets(self, user_id: int) -> int:
        """API untuk mendapatkan tiket user"""
        return self._get_user_tickets(user_id)
    
    def can_spin(self, user_id: int) -> Tuple[bool, str]:
        """Memeriksa apakah user bisa spin"""
        tickets = self._get_user_tickets(user_id)
        
        if tickets <= 0:
            return False, "❌ Anda tidak memiliki tiket lucky wheel!\nGunakan /buyticket untuk membeli tiket."
        
        if not self._check_cooldown(user_id, 'spin'):
            cooldown_end = self._get_user_cooldowns(user_id)['spin']
            remaining_seconds = int((cooldown_end - datetime.now()).total_seconds())
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return False, f"⏰ Tunggu {minutes}:{seconds:02d} lagi untuk spin berikutnya!"
        
        return True, "✅ Anda bisa spin sekarang!"
    
    def buy_ticket(self, user_id: int, amount: int, price_per_ticket: int = 25) -> Tuple[bool, str]:
        """Membeli tiket lucky wheel"""
        # Anda bisa mengganti ini dengan sistem currency yang sebenarnya
        user_balance = self.user_data.get(str(user_id), {}).get('balance', 1000)  # Default balance
        
        total_cost = amount * price_per_ticket
        
        if user_balance < total_cost:
            return False, f"❌ Saldo tidak mencukupi! Butuh {total_cost} Fizz Coin, saldo Anda: {user_balance}"
        
        # Kurangi saldo dan tambah tiket
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {}
        
        self.user_data[str(user_id)]['balance'] = user_balance - total_cost
        self._add_user_tickets(user_id, amount)
        
        return True, f"✅ Berhasil membeli {amount} tiket! Total tiket Anda: {self._get_user_tickets(user_id)}"
    
    def spin_wheel(self, user_id: int) -> Tuple[bool, str, Optional[LuckyWheelPrize]]:
        """Memutar lucky wheel"""
        can_spin_result, message = self.can_spin(user_id)
        if not can_spin_result:
            return False, message, None
        
        # Kurangi tiket
        current_tickets = self._get_user_tickets(user_id)
        if current_tickets <= 0:
            return False, "❌ Tiket tidak mencukupi!", None
        
        self._set_user_tickets(user_id, current_tickets - 1)
        
        # Set cooldown (5 menit)
        self._set_user_cooldown(user_id, 'spin', timedelta(minutes=5))
        
        # Pilih hadiah berdasarkan chance
        prize = self._select_prize()
        
        # Berikan hadiah
        self._give_prize(user_id, prize)
        
        return True, f"🎰 Lucky Wheel Spinned! 🎰", prize
    
    def _select_prize(self) -> LuckyWheelPrize:
        """Memilih hadiah berdasarkan persentase chance"""
        rand = random.uniform(0, 100)
        cumulative = 0.0
        
        for prize in self.prizes:
            cumulative += prize.chance_percentage
            if rand <= cumulative:
                return prize
        
        # Fallback ke hadiah pertama jika tidak ada yang cocok
        return self.prizes[0]
    
    def _give_prize(self, user_id: int, prize: LuckyWheelPrize):
        """Memberikan hadiah kepada user"""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {}
        
        user_data = self.user_data[str(user_id)]
        
        if prize.prize_type == PrizeType.FIZZ_COIN:
            # Tambah Fizz Coin
            current_balance = user_data.get('balance', 0)
            user_data['balance'] = current_balance + prize.value
            
        elif prize.prize_type == PrizeType.TICKET:
            # Tambah Tiket
            current_tickets = user_data.get('tickets', 0)
            user_data['tickets'] = current_tickets + prize.value
            
        elif prize.prize_type == PrizeType.HP_POTION:
            # Tambah HP (implementasi sesuai game Anda)
            current_hp = user_data.get('hp', 100)
            user_data['hp'] = min(current_hp + prize.value, 999)
            
        elif prize.prize_type == PrizeType.MP_POTION:
            # Tambah MP (implementasi sesuai game Anda)
            current_mp = user_data.get('mp', 50)
            user_data['mp'] = min(current_mp + prize.value, 999)
            
        elif prize.prize_type == PrizeType.JACKPOT:
            # Jackpot - semua Fizz Coin
            current_balance = user_data.get('balance', 0)
            user_data['balance'] = current_balance + prize.value
        
        self._save_user_data()
    
    def get_prizes_info(self) -> str:
        """Mendapatkan informasi semua hadiah"""
        info = "🎰 **DAFTAR HADIAH LUCKY WHEEL** 🎰\n\n"
        
        for prize in self.prizes:
            chance_text = f"{prize.chance_percentage:.1f}%"
            info += f"{prize.icon} **{prize.name}** - {chance_text}\n"
            info += f"   {prize.description}\n\n"
        
        info += "💡 **Cara Main:**\n"
        info += "• Gunakan `/buyticket [jumlah]` untuk membeli tiket\n"
        info += "• 1 tiket = 1x spin (25 Fizz Coin)\n"
        info += "• Cooldown 5 menit setiap spin\n"
        info += "• Tiket tidak bisa ditukar kembali\n"
        
        return info
    
    def get_user_status(self, user_id: int) -> str:
        """Mendapatkan status user"""
        tickets = self._get_user_tickets(user_id)
        balance = self.user_data.get(str(user_id), {}).get('balance', 0)
        
        status = f"🎫 **Tiket Lucky Wheel:** {tickets}\n"
        status += f"💰 **Fizz Coin:** {balance}\n"
        
        # Cek cooldown
        if not self._check_cooldown(user_id, 'spin'):
            cooldown_end = self._get_user_cooldowns(user_id)['spin']
            remaining_seconds = int((cooldown_end - datetime.now()).total_seconds())
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            status += f"⏰ **Cooldown:** {minutes}:{seconds:02d}"
        else:
            status += "✅ **Siap Spin!**"
        
        return status
    
    def admin_add_tickets(self, user_id: int, amount: int) -> bool:
        """Admin menambah tiket untuk user (untuk event atau gift)"""
        self._add_user_tickets(user_id, amount)
        return True
    
    def get_prize_by_type(self, prize_type: PrizeType) -> List[LuckyWheelPrize]:
        """Mendapatkan semua hadiah berdasarkan tipe"""
        return [prize for prize in self.prizes if prize.prize_type == prize_type]
    
    def update_prize_chance(self, prize_name: str, new_chance: float) -> bool:
        """Update persentase chance hadiah (untuk admin)"""
        for prize in self.prizes:
            if prize.name == prize_name:
                prize.chance_percentage = new_chance
                return True
        return False

# Instansi global untuk digunakan di bot
lucky_wheel_manager = LuckyWheelManager()

# Fungsi helper untuk easy integration dengan bot
def get_user_tickets(user_id: int) -> int:
    """Helper function untuk mendapatkan tiket user"""
    return lucky_wheel_manager.get_user_tickets(user_id)

def buy_lucky_wheel_ticket(user_id: int, amount: int) -> str:
    """Helper function untuk membeli tiket"""
    success, message = lucky_wheel_manager.buy_ticket(user_id, amount)
    return message

def spin_lucky_wheel(user_id: int) -> Tuple[bool, str, Optional[LuckyWheelPrize]]:
    """Helper function untuk spin lucky wheel"""
    return lucky_wheel_manager.spin_wheel(user_id)

def can_user_spin(user_id: int) -> Tuple[bool, str]:
    """Helper function untuk cek apakah user bisa spin"""
    return lucky_wheel_manager.can_spin(user_id)

def get_lucky_wheel_info() -> str:
    """Helper function untuk mendapatkan info lucky wheel"""
    return lucky_wheel_manager.get_prizes_info()

def get_user_lucky_wheel_status(user_id: int) -> str:
    """Helper function untuk mendapatkan status lucky wheel user"""
    return lucky_wheel_manager.get_user_status(user_id)

# Command handlers untuk bot (Anda bisa copy paste ke bot utama)
def handle_lucky_wheel_commands(update, context):
    """Handler untuk semua command lucky wheel"""
    command = update.message.text.split()[0].lower()
    user_id = update.message.from_user.id
    
    if command == '/spin' or command == '/luckywheel':
        # Spin lucky wheel
        success, message, prize = spin_lucky_wheel(user_id)
        
        if success and prize:
            spin_message = f"🎰 **SPIN LUCKY WHEEL!** 🎰\n\n"
            spin_message += f"{message}\n\n"
            spin_message += f"🏆 **HADIAH:**\n"
            spin_message += f"{prize.icon} **{prize.name}**\n"
            spin_message += f"✨ {prize.description}"
            
            # Tambahkan efek jackpot jika win jackpot
            if prize.prize_type == PrizeType.JACKPOT:
                spin_message += f"\n\n🎉🎉🎉 **JACKPOT!** 🎉🎉🎉"
                spin_message += f"\n🎊 Selamat! Anda mendapatkan jackpot terbesar! 🎊"
            
            update.message.reply_text(spin_message, parse_mode='Markdown')
        else:
            update.message.reply_text(message)
    
    elif command.startswith('/buyticket'):
        # Beli tiket
        try:
            parts = update.message.text.split()
            amount = int(parts[1]) if len(parts) > 1 else 1
            
            if amount <= 0:
                update.message.reply_text("❌ Jumlah tiket harus lebih dari 0!")
                return
            
            message = buy_lucky_wheel_ticket(user_id, amount)
            update.message.reply_text(message)
            
        except (IndexError, ValueError):
            update.message.reply_text("❌ Format: /buyticket [jumlah]\nContoh: /buyticket 5")
    
    elif command == '/mytickets' or command == '/tiket':
        # Lihat status tiket
        status = get_user_lucky_wheel_status(user_id)
        update.message.reply_text(status, parse_mode='Markdown')
    
    elif command == '/prizes' or command == '/hadiah':
        # Lihat daftar hadiah
        info = get_lucky_wheel_info()
        update.message.reply_text(info, parse_mode='Markdown')
    
    elif command == '/help' and 'luckywheel' in update.message.text:
        # Help lucky wheel
        help_text = "🎰 **LUCKY WHEEL COMMANDS** 🎰\n\n"
        help_text += "• `/spin` - Memutar lucky wheel (butuh 1 tiket)\n"
        help_text += "• `/buyticket [jumlah]` - Membeli tiket (25 Fizz Coin/tiket)\n"
        help_text += "• `/mytickets` - Lihat tiket dan saldo\n"
        help_text += "• `/prizes` - Lihat daftar hadiah\n"
        help_text += "• Cooldown: 5 menit setiap spin\n"
        help_text += "• Tiket tidak bisa ditukar kembali\n"
        
        update.message.reply_text(help_text, parse_mode='Markdown')

# Fungsi admin (untuk diintegrasikan dengan system admin bot)
def admin_lucky_wheel_commands(update, context):
    """Handler untuk command admin lucky wheel"""
    # Implementasi sesuai sistem admin yang ada
    pass
