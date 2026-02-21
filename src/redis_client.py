import redis.asyncio as redis
from src.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
