import jwt
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from pathlib import Path
# from src.data.state_jwt import work_to_blt, state_blt
from src.data.state_white_jwt import work_to_white
from src._exceptions.to_except import ForbiddenError


SECRET_KEY = 'secretkey'
ALGORITM = 'HS256'


class JwtWorker:
    def __init__(self, scr_key, algoritm):
        self.scr_key: str = SECRET_KEY
        self.algoritm: str = algoritm

    def creat_pair_jwt(self, login: str):
        access = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.scr_key, algorithm=self.algoritm)
        refresh = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.scr_key, algorithm=self.algoritm)
        work_to_white.set_state(login, access)
        work_to_white.set_state(login, refresh)
        return {'access': access,
                'refresh': refresh}

    def loging(self, access):
        try:
            payload = jwt.decode(access, self.scr_key, algorithms=self.algoritm)
            if payload.get('login'):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
            # return {'Error': 'ExpiredSignatureError'}
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
            # return {'Error': 'InvalidTokenError'}

    def get_user_from_access(self, access):
        try:
            payload = jwt.decode(access, self.scr_key, algorithms=self.algoritm)
            if payload.get('login'):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
            # return {'Error': 'ExpiredSignatureError'}
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
            # return {'Error': 'InvalidTokenError'}

    def get_user_from_refresh(self, refresh):
        try:
            payload = jwt.decode(refresh, self.scr_key, algorithms=self.algoritm)
            if work_to_blt.get_state(refresh, payload.get('login')):
                    work_to_blt.set_state(payload.get('login'), refresh)
                    return self.creat_pair_jwt(payload.get('login'))
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
            # return {'Error': 'ExpiredSignatureError'}
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
            # return {'Error': 'InvalidTokenError'}
        else:
            raise ForbiddenError('Token to Black List.')
            # return {'Error': 'Token to Black List.'}

jwt_work = JwtWorker(SECRET_KEY, ALGORITM)