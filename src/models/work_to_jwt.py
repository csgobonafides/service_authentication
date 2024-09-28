import jwt
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from src.data.state_jwt import wotk_to_blt, state_blt

SECRET_KEY = 'secretkey'
ALGORITM = 'HS256'


class JwtWorker:
    def __init__(self, scr_key, algoritm):
        self.scr_key: str = SECRET_KEY
        self.algoritm: str = algoritm

    def creat_pair_jwt(self, login: dict):
        access = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.scr_key, algorithm=self.algoritm)
        refresh = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.scr_key, algorithm=self.algoritm)
        return {'access': access,
                'refresh': refresh}

    def get_user_from_access(self, access):
        try:
            payload = jwt.decode(access, self.scr_key, algorithms=self.algoritm)
            if payload.get('login'):
                return True
        except jwt.ExpiredSignatureError:
            return {'Error': 'ExpiredSignatureError'}
        except jwt.InvalidTokenError:
            return {'Error': 'InvalidTokenError'}

    def get_user_from_refresh(self, refresh):
        try:
            payload = jwt.decode(refresh, self.scr_key, algorithms=self.algoritm)
            if payload.get('login'):
                wotk_to_blt.set_state(payload.get('login'), refresh)
                return self.creat_pair_jwt(payload.get('login'))
        except jwt.ExpiredSignatureError:
            return {'Error': 'ExpiredSignatureError'}
        except jwt.InvalidTokenError:
            return {'Error': 'InvalidTokenError'}