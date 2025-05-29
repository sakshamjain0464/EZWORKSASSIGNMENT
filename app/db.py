# app/db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = db = client["ezworks"]

def connect_db():
    try:
        client.admin.command('ping')
        print("✅ MongoDB Atlas connected")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
