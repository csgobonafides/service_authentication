import abc
from typing import Any
import json
from src._exceptions.to_except import BadRequestError


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



class JsonFileStorage(CacheStorage):
    def __init__(self, file_path = None):
        self.file_path = file_path
        self.data = {}

    async def connect(self):
        if self.file_path is None:
            return

        with open(self.file_path, 'r') as file:
            self.data = json.load(file)

    async def disconnect(self):
        if self.file_path is None:
            return
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file)

    async def add(self, key: str, value: Any) -> None:
        if key in self.data:
            raise BadRequestError('Ключ уже существует.')
        self.data[key] = value

    async def get(self, key: str):
        if key not in self.data:
            raise ValueError("Такого ключа не найдено.")
        return self.data[key]

    async def update(self, key: str, value: Any) -> None:
        if key not in self.data:
            raise ValueError('Такого ключа не найдено.')
        self.data[key] = value

    async def delete(self, key: str) -> None:
        if key not in self.data:
            raise ValueError('Такого ключа не найдено.')
        self.data.pop(key)

    async def delete_value(self, key: str) -> None:
        if key not in self.data:
            raise ValueError('Такого ключа не найдено.')
        self.data[key].clear()