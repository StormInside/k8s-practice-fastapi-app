from default_settings import REDIS_HOST, REDIS_PORT, REDIS_DB, CACHE_TIMEOUT, DEFAULT_POSTGRES_WRITE_URL, DEFAULT_POSTGRES_READ_URL
import os

REDIS_HOST = os.getenv("REDIS_HOST", REDIS_HOST)
REDIS_PORT = int(os.getenv("REDIS_PORT", REDIS_PORT))
REDIS_DB = int(os.getenv("REDIS_DB", REDIS_DB))
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", CACHE_TIMEOUT))
POSTGRES_WRITE_URL = os.getenv("POSTGRES_WRITE_URL", DEFAULT_POSTGRES_WRITE_URL)
POSTGRES_READ_URL = os.getenv("POSTGRES_READ_URL", DEFAULT_POSTGRES_READ_URL)