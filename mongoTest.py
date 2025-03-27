# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv
# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# DB_NAME = os.getenv("DB_NAME", "bookify")
# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
from utils import get_db_handle
db, client = get_db_handle()

# List all collections in the database
print("Collections:", db.list_collection_names())
