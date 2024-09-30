import abc
import json
import logging
from typing import Any, Optional
from pathlib import Path
from pydantic import BaseModel

db_logger = logging.getLogger('State to db.')
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=Path(__file__).parent.parent.parent /'example.log',
                    level=logging.DEBUG)


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
            db_logger.warning('No state file provided. Continue with in-memory state')
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
            db_logger.info(f'Пользователь с логином {login} уже зарегистрирован.')
            return {'message': 'Пользователь с таким логином уже зарегистрирован.'}
        else:
            self.state[login] = psw
            self.storage.save_state(self.state)
            db_logger.info('Set key-login \'%s\' with value-password \'%s\' to sorage', login, psw)
            return {'message': 'Пользователь успешно зарегистрирован.'}

    '''Проверяет, есть ли уже такой пользователь.'''
    def chek_user(self, login: str) -> Any:
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
