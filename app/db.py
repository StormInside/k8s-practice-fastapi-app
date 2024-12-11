from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.models import Base

# Read database URLs from environment variables
POSTGRES_WRITE_URL = os.getenv("POSTGRES_WRITE_URL")
if not POSTGRES_WRITE_URL:
    from app.default_settings import DEFAULT_POSTGRES_WRITE_URL
    POSTGRES_WRITE_URL = DEFAULT_POSTGRES_WRITE_URL
POSTGRES_READ_URL = os.getenv("POSTGRES_READ_URL")
if not POSTGRES_READ_URL:
    from app.default_settings import DEFAULT_POSTGRES_READ_URL
    POSTGRES_READ_URL = DEFAULT_POSTGRES_READ_URL


# SQLAlchemy setup for write operations
engine_write = create_async_engine(POSTGRES_WRITE_URL, echo=True)
SessionLocalWrite = sessionmaker(bind=engine_write, class_=AsyncSession, expire_on_commit=False)

# SQLAlchemy setup for read operations
engine_read = create_async_engine(POSTGRES_READ_URL, echo=True)
SessionLocalRead = sessionmaker(bind=engine_read, class_=AsyncSession, expire_on_commit=False)

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


if __name__ == "__main__":

    from models import User
    import asyncio

    async def test():
        # Create a new user

        await create_db_and_tables()

        async with SessionLocalWrite() as session:
            new_user = User(name="Alice", email="test.com")
            session.add(new_user)

            await session.commit()

            print(new_user.id)
            print(new_user.name)
            print(new_user.email)

    asyncio.run(test())

