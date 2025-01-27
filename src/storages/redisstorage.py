from storages.base import CacheStorage
import redis.asyncio as redis
import json

from core.exceptions import NotFoundError, ForbiddenError, UnauthorizedError

REFRESH_EXPIRES = 600
ACCESS_EXPIRES = 60


class RedisStorage(CacheStorage):

    def __init__(self,  host='redis', port=6379):
        self.redis = None
        self.host = host
        self.port = port

    def connect(self):
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            db=0
        )

    async def disconnect(self):
        await self.redis.aclose()

    async def _revoke_token(self,
                            jwt: str,
                            pipeline:
                            redis.client.Pipeline,
                            refresh: bool
                            ) -> None:
        expires = REFRESH_EXPIRES if refresh else ACCESS_EXPIRES
        await pipeline.setex(jwt, expires, 'black')

    async def revoke_token(self,
                           jwt: str,
                           refresh: bool = False
                           ) -> None:
        pair_jwt = await self.redis.get(jwt)
        pipeline = self.redis.pipeline()

        if pair_jwt and pair_jwt != b'black':
            await self._revoke_token(pair_jwt, pipeline, refresh=not refresh)

        await self._revoke_token(jwt, pipeline, refresh=refresh)
        await pipeline.execute()

    async def add(self,
                  user_id: str,
                  access_jwt: str,
                  refresh_jwt: str,
                  user_agent: str
                  ) -> bool:
        user_tokens = json.loads(await self.redis.get(user_id) or '{}')
        pipeline = await self.redis.pipeline()
        old_token = user_tokens.get(user_agent)
        if old_token:
            await self.revoke_token(old_token, refresh=True)
        user_tokens[user_agent] = refresh_jwt

        await pipeline.setex(user_id, REFRESH_EXPIRES, json.dumps(user_tokens))
        await pipeline.setex(access_jwt, ACCESS_EXPIRES, refresh_jwt)
        await pipeline.setex(refresh_jwt, REFRESH_EXPIRES, access_jwt)
        await pipeline.execute()
        return True

    async def get(self, jwt: str) -> bool:
        if not await self.redis.get(jwt):
            raise NotFoundError('No such key found.')
        if await self.redis.get(jwt) == b'black':
            raise ForbiddenError('Token is blacklisted.')
        else:
            return True

    async def update(self,
                     user_id: str,
                     access_jwt: str,
                     refresh_jwt: str,
                     user_agent: str
                     ) -> bool:
        user_tokens = json.loads(await self.redis.get(user_id) or '{}')

        pipeline = await self.redis.pipeline()
        old_refresh = user_tokens.get(user_agent)
        if old_refresh and await self.redis.get(old_refresh) == b'black':
            raise ForbiddenError('Token is blacklisted.')
        if old_refresh and await self.redis.get(old_refresh) != b'black':
            await self.revoke_token(old_refresh, refresh=True)

        user_tokens[user_agent] = refresh_jwt

        await pipeline.setex(user_id, REFRESH_EXPIRES, json.dumps(user_tokens))
        await pipeline.setex(access_jwt, ACCESS_EXPIRES, refresh_jwt)
        await pipeline.setex(refresh_jwt, REFRESH_EXPIRES, access_jwt)
        await pipeline.execute()
        return True

    async def delete(self, user_id: str) -> bool:
        user_tokens = json.loads(await self.redis.get(user_id) or '{}')
        pipeline = await self.redis.pipeline()
        if user_tokens != {}:
            for refresh_jwt in user_tokens.values():
                await self.revoke_token(refresh_jwt, refresh=True)
            await pipeline.delete(user_id)
            await pipeline.execute()
            return True
        else:
            raise UnauthorizedError('Not authentication.')
