from fastapi import FastAPI, Depends
from sqlalchemy.future import select
from pydantic import BaseModel
from contextlib import asynccontextmanager

from app.db import (
    get_db_read,
    get_db_write,
    create_db_and_tables,
)
from app.models import User
from app.cache import mongo_collection


# Pydantic model for user input validation
class UserCreate(BaseModel):
    name: str
    email: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Endpoint to create a new user (Write Operation)
@app.post("/users/")
async def create_user(user: UserCreate, db=Depends(get_db_write)):
    # Check if user is in MongoDB cache
    # cached_user = await mongo_collection.find_one({"email": user.email})
    # if cached_user:
    #     return {"message": "User already exists in cache", "user": cached_user}

    # Check if user exists in PostgreSQL
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        # Cache the user in MongoDB
        # await mongo_collection.insert_one({"email": existing_user.email, "name": existing_user.name})
        return {"message": "User already exists in database", "user": {"email": existing_user.email, "name": existing_user.name}}

    # Create new user in PostgreSQL
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Cache the new user in MongoDB
    # await mongo_collection.insert_one({"email": new_user.email, "name": new_user.name})

    return {"message": "User created", "user": {"email": new_user.email, "name": new_user.name}}

# Endpoint to retrieve a user (Read Operation)
@app.get("/users/{user_email}")
async def read_user(user_email: str, db=Depends(get_db_read)):
    # Check MongoDB cache first
    # cached_user = await mongo_collection.find_one({"email": user_email})
    # if cached_user:
    #     return {"user": cached_user}

    # Retrieve user from PostgreSQL if not in cache
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalars().first()
    if user:
        # Cache the user in MongoDB
        # await mongo_collection.insert_one({"email": user.email, "name": user.name})
        return {"user": {"email": user.email, "name": user.name}}
    else:
        return {"message": "User not found"}

@app.get("/users")
async def read_user(db=Depends(get_db_read)):

    # Retrieve user from PostgreSQL if not in cache
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"users": users}
