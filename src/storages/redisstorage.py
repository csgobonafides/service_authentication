from src.storages.base import CacheStorage
import redis.asyncio as redis
from typing import Any

class RedisStorage(CacheStorage):

    def __init__(self,  host='localhost', port=6379):
        self.redis = None
        self.host = host
        self.port = port

    async def connect(self):
        self.redis = redis.Redis(host=self.host, port=self.port)

    async def disconnect(self):
        await self.redis.close()

    async def add(self, key: str, value: Any):
        if self.redis.lrange(key, 0, -1):
            raise ValueError('ключ уже существует')
        await self.redis.rpush(key, *value)

    async def get(self, key: str):
        if not self.redis.lrange(key, 0, -1):
            raise ValueError('Такого ключа не найдено')
        await self.redis.lrange(key, 0, -1)

    async def update(self, key: str, value: Any):
        if not self.redis.lrange(key, 0, -1):
            raise ValueError('Такого ключа не найдено')
        await self.redis.rpush(key, value)

    async def delete(self, key: str):
        if not self.redis.lrange(key, 0, -1):
            raise ValueError('Такого ключа не найдено')
        await self.redis.delete(key)