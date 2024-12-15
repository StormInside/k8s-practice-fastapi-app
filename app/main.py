from fastapi import FastAPI, Depends, Request
from sqlalchemy.future import select
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging


from app.db import (
    get_db_read,
    get_db_write,
    create_db_and_tables,
)

from app.models import User
from app.cache import RedisCache


logger = logging.getLogger("uvicorn.error")

class UserCreate(BaseModel):
    name: str
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await create_db_and_tables()

    # Initialize and connect Redis cache
    cache = RedisCache(host="localhost", port=6379, db=0)
    try:
        await cache.connect()
        app.state.cache = cache
    except Exception as e:
        # Could not connect to Redis, log a warning and continue
        logger.warning(f"Failed to connect to Redis: {e}. Continuing without cache.")
        app.state.cache = None  # No cache available

    yield

    # Close Redis connection on shutdown
    if app.state.cache:
        await app.state.cache.close()


app = FastAPI(lifespan=lifespan)


def get_cache(request: Request) -> RedisCache:
    # Dependency to retrieve the cache from app.state
    return request.app.state.cache


@app.post("/users/")
async def create_user(user: UserCreate, db=Depends(get_db_write), cache: RedisCache = Depends(get_cache)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        return {"message": "User already exists in database", "user": {"email": existing_user.email, "name": existing_user.name}}

    # Create new user in PostgreSQL
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Cache the new user in Redis if cache is available
    if cache:
        await cache.put_user(new_user.email, {"email": new_user.email, "name": new_user.name})

    return {"message": "User created", "user": {"email": new_user.email, "name": new_user.name}}

@app.get("/users/{user_email}")
async def read_user(user_email: str, db=Depends(get_db_read), cache: RedisCache = Depends(get_cache)):
    # Check Redis first if available
    if cache:
        cached_user = await cache.get_user(user_email)
        if cached_user:
            return {"user": cached_user}

    # If not in cache or no cache, fetch from DB
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalars().first()
    if user:
        user_data = {"email": user.email, "name": user.name}
        # Store in redis if available
        if cache:
            await cache.put_user(user.email, user_data)
        return {"user": user_data}
    else:
        return {"message": "User not found"}

@app.get("/users")
async def read_users(db=Depends(get_db_read)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"users": [{"email": u.email, "name": u.name} for u in users]}
