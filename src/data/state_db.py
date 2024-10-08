import abc
import json
from typing import Any, Optional
from pathlib import Path
from pydantic import BaseModel


class User(BaseModel):
    login: str
    password: str


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict):
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    '''Сохраняет данные в файл'''
    def save_state(self, state: dict):
        if self.file_path is None:
            return False

        with open(self.file_path, 'w') as f:
            json.dump(state, f)

    '''Показывает данные всего файла'''
    def retrieve_state(self) -> Optional[dict]:
        if self.file_path is None:
            return False

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            self.save_state({})
        return


'''Registration User to Data Base'''
class Registration:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = storage.retrieve_state() or {}

    '''Сохраняет логин и пороль в базе.'''
    def set_user(self, login: str, psw: str):
        if self.state.get(login):
            return {'message': 'Пользователь с таким логином уже зарегистрирован.'}
        else:
            self.state[login] = psw
            self.storage.save_state(self.state)
            return {'message': 'Пользователь успешно зарегистрирован.'}

    '''Проверяет, есть ли уже такой пользователь.'''
    def chek_user(self, login: str) -> Any:
        self.state = self.storage.retrieve_state() or {}
        if self.state.get(login):
            return False
        else:
            return True

    def check_psw(self, login: str, psw: str) -> Any:
        if not self.chek_user(login) and self.state.get(login) == psw:
            return True
        else:
            return False

dir = Path(__file__).parent.parent.parent
db_path = dir /'db.json'

state_db = JsonFileStorage(db_path)
work_to_user = Registration(state_db)
