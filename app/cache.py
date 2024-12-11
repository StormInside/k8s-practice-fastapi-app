import os
import motor.motor_asyncio

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# MongoDB setup
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client["cache_db"]
mongo_collection = mongo_db["cache_collection"]

