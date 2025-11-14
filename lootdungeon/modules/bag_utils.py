import json, os

BAG_FOLDER = "data/bags/"
os.makedirs(BAG_FOLDER, exist_ok=True)

def load_bag(user_id):
    path = f"{BAG_FOLDER}bag_{user_id}.json"
    if not os.path.exists(path):
        # default bag kosong
        bag = {"Fizz Coin":0, "Monster Drop":{}, "Equipment Drop":{}, "Card Drop":{}}
        save_bag(user_id, bag)
        return bag
    with open(path,"r") as f:
        return json.load(f)

def save_bag(user_id, bag):
    path = f"{BAG_FOLDER}bag_{user_id}.json"
    with open(path,"w") as f:
        json.dump(bag,f,indent=2)
