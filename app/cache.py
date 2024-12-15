import json
import redis.asyncio as redis

from app.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, CACHE_TIMEOUT


class RedisCache:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        self.host = host
        self.port = port
        self.db = db
        self.client = None

    async def connect(self):
        if self.client is None:
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db)
            await self.client.ping()

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def put_user(self, user_email: str, user_data: dict):
        if self.client:
            await self.client.set(f"user:{user_email}", json.dumps(user_data), expire=CACHE_TIMEOUT)

    async def get_user(self, user_email: str):
        if not self.client:
            return None
        data = await self.client.get(f"user:{user_email}")
        if data:
            return json.loads(data)
        return None
