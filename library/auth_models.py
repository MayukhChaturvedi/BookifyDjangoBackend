# library/auth_models.py
from utils import get_db_handle
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from .mongodb import users_col

class User:
    @staticmethod
    def create_user(username, email, password):
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "email": email, "password": hashed_password}
        result = users_col.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_username(username):
        return users_col.find_one({"username": username})

    @staticmethod
    def find_by_id(user_id):
        return users_col.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def check_password(stored_password, password):
        return check_password_hash(stored_password, password)