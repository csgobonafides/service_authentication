from src.storages.base import CacheStorage
import redis.asyncio as redis
from typing import Any
import json

REFRESH_EXPIRES = 600
ACCESS_EXPIRES = 60

class RedisStorage(CacheStorage):

    def __init__(self,  host = 'localhost', port = 6379):
        self.redis: redis.Redis = None
        self.host = host
        self.port = port

    async def connect(self):
        self.redis = redis.Redis(host=self.host, port=self.port)

    async def disconnect(self):
        await self.redis.close()

    async def _revoke_token(self, jwt: str, pipeline: redis.client.Pipeline, refresh: bool) -> None:
        expires = REFRESH_EXPIRES if refresh else ACCESS_EXPIRES
        await pipeline.setex(jwt, expires, 'black')

    async def revoke_token(self, jwt: str, refresh: bool = False):
        pair_jwt = self.redis.get(jwt)
        pipeline = self.redis.pipeline()

        if pair_jwt and pair_jwt != b'black':
            await self._revoke_token(pair_jwt, pipeline, refresh=not refresh)

        await self._revoke_token(jwt, pipeline, refresh=refresh)
        await pipeline.execute()

    async def add(self, user_id: str, access_jwt: str, refresh_jwt: str, user_agent: str) -> None:
        user_tokens = json.loads(await self.redis.get(user_id) or {})

        pipeline = await self.redis.pipeline()
        old_refresh = await user_tokens.get(user_agent)
        if old_refresh:
            await self.revoke_token(old_refresh, refresh=True)

        user_tokens[user_agent] = refresh_jwt

        await pipeline.setex(user_id, REFRESH_EXPIRES, json.dumps(user_tokens))
        await pipeline.setex(access_jwt, ACCESS_EXPIRES, refresh_jwt)
        await pipeline.setex(refresh_jwt, REFRESH_EXPIRES, access_jwt)
        await pipeline.execute()


    async def get(self, jwt: str):
        if not await self.redis.get(jwt):
            raise ValueError('Такого ключа не найдено')
        if await self.redis.get(jwt) == b'black':
            raise ValueError('Токен в черном списке')
        else:
            return True

    async def update(self, user_id: str, access_jwt: str, refresh_jwt: str, user_agent: str):
        user_tokens = json.loads(await self.redis.get(user_id) or {})

        pipeline = await self.redis.pipeline()
        old_refresh = await user_tokens.get(user_agent)
        if old_refresh and await self.redis.get(old_refresh) != b'black':
            await self.add(user_id, access_jwt, refresh_jwt, user_agent)
            return True
        else:
            raise ValueError('Токен в черном списке')


    async def delete(self, user_id: str):
        user_tokens = json.loads(await self.redis.get(user_id) or {})
        pipeline = await self.redis.pipeline()
        for refresh_jwt in user_tokens.values():
            await self.revoke_token(refresh_jwt, refresh=True)
        await pipeline.delete(user_id)
        await pipeline.execute()
        return True