from typing import Any
import json
from src.core.exceptions import NotFoundError, ForbiddenError
from src.storages.base import CacheStorage


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
            raise ForbiddenError('Ключ уже существует.')
        self.data[key] = value

    async def get(self, key: str):
        if key not in self.data:
            raise NotFoundError("Такого ключа не найдено.")
        return self.data[key]

    async def update(self, key: str, value: Any) -> None:
        if key not in self.data:
            raise NotFoundError('Такого ключа не найдено.')
        self.data[key] = value

    async def delete(self, key: str) -> None:
        if key not in self.data:
            raise NotFoundError('Такого ключа не найдено.')
        self.data.pop(key)

    async def delete_value(self, key: str) -> None:
        if key not in self.data:
            raise NotFoundError('Такого ключа не найдено.')
        self.data[key].clear()
