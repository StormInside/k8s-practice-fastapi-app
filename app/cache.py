import json
import os

import redis.asyncio as redis

def get_redis_settings():
    from app.settings import REDIS_PORT, REDIS_DB, CACHE_TIMEOUT, REDIS_SERVICE

    POD_NAME = os.getenv("POD_NAME", None)  # e.g. "myrelease-fastapi-0"

    if POD_NAME:
        NAMESPACE = os.getenv("NAMESPACE")  # e.g. "default"
        REDIS_SERVICE = os.getenv("REDIS_SERVICE")  # e.g. "myrelease-redis"

        # Extract the ordinal by splitting on '-'
        # For "myrelease-fastapi-0", split by '-' gives ["myrelease", "fastapi", "0"]
        ordinal = POD_NAME.split('-')[-1]

        REDIS_HOST = f"{REDIS_SERVICE}-{ordinal}.{REDIS_SERVICE}.{NAMESPACE}.svc.cluster.local"
    else:

        REDIS_HOST = os.getenv("REDIS_SERVICE", REDIS_SERVICE)

    return {"host": REDIS_HOST, "port": REDIS_PORT, "db": REDIS_DB, "cache_timeout": CACHE_TIMEOUT}

class RedisCache:
    def __init__(self):
        settings = get_redis_settings()
        print(f"RedisCache init params: {settings['host']}:{settings['port']}/{settings['db']} with cache timeout {settings['cache_timeout']}")
        self.host = settings["host"]
        self.port = settings["port"]
        self.db = settings["db"]
        self.client = None
        self.cache_timeout = settings["cache_timeout"]

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
            await self.client.set(f"user:{user_email}", json.dumps(user_data), ex=self.cache_timeout)

    async def get_user(self, user_email: str):
        if not self.client:
            return None
        data = await self.client.get(f"user:{user_email}")
        if data:
            return json.loads(data)
        return None
