import abc
from typing import Any


class BaseStorage:

    @abc.abstractmethod
    async def connect(self) -> None:
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        pass


class CacheStorage(BaseStorage):

    @abc.abstractmethod
    async def add(self, user_id: str, access_jwt: str, refresh_jwt: str, user_agent: str) -> None:
        pass

    @abc.abstractmethod
    async def get(self, key: str) -> dict:
        pass

    @abc.abstractmethod
    async def update(self, user_id: str, access_jwt: str, refresh_jwt: str, user_agent: str) -> None:
        pass

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        pass
