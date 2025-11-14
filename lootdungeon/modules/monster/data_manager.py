#ATA/modules/monster/data_manager.py
import os
import json
from threading import Lock

DB_FILE = "data/bag_data.json"
LOCK = Lock()

# Pastikan folder data ada
if not os.path.exists("data"):
    os.makedirs("data")

# Inisialisasi file JSON jika belum ada
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)


def load_inventory():
    """Load seluruh data inventory"""
    with LOCK:
        with open(DB_FILE, "r") as f:
            return json.load(f)


def save_inventory(data):
    """Simpan data inventory ke file"""
    with LOCK:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)


def add_drop(player_id, drop_name, amount):
    """Tambahkan drop ke player, Fizz Coin selalu di atas"""
    data = load_inventory()
    player_id = str(player_id)
    if player_id not in data:
        data[player_id] = []

    # Fizz Coin selalu di atas
    if drop_name.lower() == "fizz coin":
        data[player_id] = [{"item": drop_name, "amount": amount}] + data[player_id]
    else:
        data[player_id].append({"item": drop_name, "amount": amount})

    save_inventory(data)


def get_inventory(player_id):
    """Ambil inventory player"""
    data = load_inventory()
    return data.get(str(player_id), [])
