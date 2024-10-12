import abc
import json
from typing import Any, Optional
from pathlib import Path


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorageJWT(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    '''Сохраняет данные в файл'''
    def save_state(self, state: dict) -> None:
        if self.file_path is None:
            return

        with open(self.file_path, 'w') as f:
            json.dump(state, f)

    '''Показывает данные всего файла'''
    def retrieve_state(self) -> Optional[dict]:
        if self.file_path is None:
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            self.save_state({})
        return


class StateJWT(BaseStorage):
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = storage.retrieve_state() or {}

    '''Сохраняет токен с ключем-логином'''
    def set_state(self, key: str, value) -> None:
        if self.state.get(key):
            if type(value) == list:
                a = self.state.get(key) + value
                self.state[key] = a
                self.storage.save_state(self.state)
            else:
                self.state[key].append(value)
                self.storage.save_state(self.state)
        else:
            self.state[key] = [value]
            self.storage.save_state(self.state)

    '''Показывает токен по ключу-логину'''
    def get_state(self, refresh: str, key: str) -> Any:
        if self.state.get(key) == None or refresh not in self.state.get(key):
            return True
        else:
            return False



# dir = Path(__file__).parent.parent.parent
# blt_path = dir /'black_token.json'
# state_blt = JsonFileStorageJWT(dir /'black_token.json')
# work_to_blt = StateJWT(state_blt)