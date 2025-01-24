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
    async def add(self, key: str, value: Any) -> None:
        pass

    @abc.abstractmethod
    async def get(self, key: str) -> dict:
        pass

    @abc.abstractmethod
    async def update(self, key: str, value: Any) -> None:
        pass

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        pass
