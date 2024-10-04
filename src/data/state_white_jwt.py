import abc
import json
from typing import Any, Optional
from pathlib import Path
from src.data.state_jwt import work_to_blt



class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorage(BaseStorage):
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


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = storage.retrieve_state() or {}

    '''Сохраняет токен с ключем-логином'''
    def set_state(self, key: str, value: str) -> None:
        if self.state.get(key):
            self.state[key].append(value)
            self.storage.save_state(self.state)
        else:
            self.state[key] = [value]
            self.storage.save_state(self.state)


    def delet_tokens(self, login: str):
        if self.state.get(login):
            work_to_blt.set_state(login, self.state.get(login))
            self.state.get(login).clear()
            self.storage.save_state(self.state)
        else:
            return None



dir = Path(__file__).parent.parent.parent
white_path = dir /'white_token.json'

state_white = JsonFileStorage(white_path)
work_to_white = State(state_white)
