import random

def get_floor1_monsters():
    return [
        {"name": "Fabre","level":1,"hp":10,"atk":[1,2],"def":1,"mdef":0,"base_exp":2.0,"base_coin":5,"chance":70,"equipment_drop":["IRON HELMET"]},
        {"name": "Barachi","level":2,"hp":20,"atk":[2,4],"def":2,"mdef":1,"base_exp":3.0,"base_coin":7,"chance":20,"equipment_drop":["IRON BOOT"]},
        {"name": "Fungus","level":3,"hp":20,"atk":[5,8],"def":1,"mdef":2,"base_exp":5.0,"base_coin":10,"chance":10,"equipment_drop":["IRON ARMOR"]}
    ]

def find_floor1_monster(hero_level=None):
    """Pilih monster dari floor 1 (weighted chance)."""
    monsters = get_floor1_monsters()
    if not monsters:
        return None
    total_chance = sum(m["chance"] for m in monsters)
    roll = random.uniform(0, total_chance)
    cumulative = 0
    for m in monsters:
        cumulative += m["chance"]
        if roll <= cumulative:
            return m
    return random.choice(monsters)

def handle_find_monster(*args, **kwargs):
    """Kembalikan dict monster dengan key 'monster' supaya menu_C.py kompatibel"""
    monster = find_floor1_monster()
    if not monster:
        return None
    return {"monster": monster}

def drop_floor1_equipment(monster):
    if "equipment_drop" not in monster or not monster["equipment_drop"]:
        return None
    if random.randint(1,100) <= 50:
        return random.choice(monster["equipment_drop"])
    return None

