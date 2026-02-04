from motor.motor_asyncio import AsyncIOMotorClient

import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "kanthalloor_db")

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DB_NAME]
        print("Connected to MongoDB")

    async def close_database_connection(self):
        self.client.close()
        print("Closed MongoDB connection")

db = Database()

async def get_database():
    return db.db
