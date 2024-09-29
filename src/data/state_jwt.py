import abc
import json
import logging
from typing import Any, Optional
from pathlib import Path

jwt_logger = logging.getLogger('State to black_token')
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=Path(__file__).parent.parent.parent /'example.log',
                    level=logging.DEBUG)

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
            jwt_logger.warning('No state file provided. Continue with in-memory state')
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
            jwt_logger.info('Set key \'%s\' with value \'%s\' to sorage', key, value)
        else:
            self.state[key] = [value]
            self.storage.save_state(self.state)
            jwt_logger.info('Set key \'%s\' with value \'%s\' to sorage', key, value)

    '''Показывает токен по ключу-логину'''
    def get_state(self, key: str) -> Any:
        return self.state.get(key)


dir = Path(__file__).parent.parent.parent
blt_path = dir /'black_token.json'

state_blt = JsonFileStorage(blt_path)
work_to_blt = State(state_blt)