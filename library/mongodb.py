# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# DB_NAME = os.getenv("DB_NAME", "library_db")

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]

from utils import get_db_handle
db, client = get_db_handle()

# Collections
authors_col = db["authors"]
books_col = db["books"]
genres_col = db["genres"]
book_instances_col = db["book_instances"]
users_col = db["users"]
