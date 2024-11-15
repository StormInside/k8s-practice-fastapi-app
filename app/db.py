from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import motor.motor_asyncio
import os

# Read database URLs from environment variables
POSTGRES_WRITE_URL = os.getenv("POSTGRES_WRITE_URL")
POSTGRES_READ_URL = os.getenv("POSTGRES_READ_URL")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# SQLAlchemy setup for write operations
engine_write = create_async_engine(POSTGRES_WRITE_URL, echo=True)
SessionLocalWrite = sessionmaker(bind=engine_write, class_=AsyncSession, expire_on_commit=False)

# SQLAlchemy setup for read operations
engine_read = create_async_engine(POSTGRES_READ_URL, echo=True)
SessionLocalRead = sessionmaker(bind=engine_read, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# MongoDB setup
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client["cache_db"]
mongo_collection = mongo_db["cache_collection"]

# Dependency to get write session
async def get_db_write():
    async with SessionLocalWrite() as session:
        yield session

# Dependency to get read session
async def get_db_read():
    async with SessionLocalRead() as session:
        yield session

# Function to create tables
async def create_db_and_tables():
    async with engine_write.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
