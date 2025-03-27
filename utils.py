from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

def get_db_handle():
    host = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "library_db")
    client = MongoClient(host)
    db_handle = client[db_name]
    username = os.getenv("USER")
    password = os.getenv("PASSWORD")
    port = os.getenv("PORT")
    if username and password and port:
        client = MongoClient(host=host,
                            port=int(port),
                            username=username,
                            password=password
                            )
        db_handle = client[db_name]
    return db_handle, client