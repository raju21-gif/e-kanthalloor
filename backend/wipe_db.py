import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def wipe():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["e-panchayat"]
    
    # Delete All
    result = await db["applications"].delete_many({})
    print(f"Deleted {result.deleted_count} applications from database.")

if __name__ == "__main__":
    asyncio.run(wipe())
