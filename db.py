from pymongo import MongoClient

client = MongoClient("mongodb://0.0.0.0:27017/")
db = client['game_recommender']
users = db['users']

def get_or_create_user(email):
    user = users.find_one({'email': email})
    if not user:
        users.insert_one({'email': email, 'purchases': []})
        user = users.find_one({'email': email})
    return user

def update_user_purchases(email, new_ids):
    users.update_one({'email': email}, {'$addToSet': {'purchases': {'$each': new_ids}}})

def get_user_purchases(email):
    user = users.find_one({'email': email})
    return user.get('purchases', []) if user else []
