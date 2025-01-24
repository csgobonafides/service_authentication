import jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
from fastapi import Request

from src.core.exceptions import ForbiddenError, UnauthorizedError, NotFoundError
from src.storages.jsonfilestorage import JsonFileStorage
from src.storages.redisstorage import RedisStorage

load_dotenv()


class Conntroller:
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITM = os.getenv('ALGORITM')
    def __init__(self, user_db, redis_db):
        self.user_db: JsonFileStorage = user_db
        self.redis_db: RedisStorage = redis_db

    async def registr(self, login: str, psw: str):
        id = await self.user_db.get('id')
        id = str(int(id) + 1)
        await self.user_db.update('id', id)
        await self.user_db.add(login, [id, psw])
        return {'status': '200'}

    async def authentication(self, login: str, psw: str, request: Request):
        if await self.user_db.get(login):
            data = await self.user_db.get(login)
            if data[1] == psw:
                us_ag = request.headers.get('User-Agent')
                result = await self.creat_pair_jwt(login, data[0])
                if await self.redis_db.add(data[0], result[0], result[1], us_ag):
                    return {'access': result[0], 'refresh': result[1]}
            else:
                raise UnauthorizedError('the password is incorrect')
        else:
            raise UnauthorizedError('user not found')

    async def creat_pair_jwt(self, login: str, user_id: str) -> list:
        access = jwt.encode({'login': login, 'id': user_id, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        refresh = jwt.encode({'login': login, 'id': user_id, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        return [access, refresh]

    def loging(self, access):
        try:
            payload = jwt.decode(access, self.SECRET_KEY, algorithms=self.ALGORITM)
            if payload.get('login'):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')

    async def get_user_from_access(self, access):
        try:
            payload = jwt.decode(access, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.redis_db.get(access):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
        else:
            raise NotFoundError('Token missing')

    async def get_user_from_refresh(self, refresh, request: Request):
        try:
            payload = jwt.decode(refresh, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.redis_db.get(refresh):
                user_ag = request.headers.get('User-Agent')
                user_id = payload.get('id')
                result = await self.creat_pair_jwt(payload.get('login'), user_id)
                if await self.redis_db.update(user_id, result[0], result[1], user_ag):
                    return {'access': result[0], 'refresh': result[1]}
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
        else:
            raise ForbiddenError('Token to Black List.')


    async def access_head(self, request: Request):
        if request.headers.get('authorization'):
            result = await self.get_user_from_access(request.headers.get('authorization')[7:])
            return result
        else:
            raise NotFoundError('Token missing')

    async def refresh_head(self, request: Request):
        if request.headers.get('refresh'):
            result = await self.get_user_from_refresh(request.headers.get('refresh'), request)
            return result
        else:
            raise NotFoundError('Token missing')

    async def login_from_del(self, request):
        if request.headers.get('authorization'):
            result_log = self.loging(request.headers.get('authorization')[7:])
            if result_log != {'Error': 'ExpiredSignatureError'} and result_log != {'Error': 'InvalidTokenError'}:
                payload = jwt.decode(request.headers.get('authorization')[7:], self.SECRET_KEY, algorithms=self.ALGORITM)
                user_id = payload.get('id')
                if await self.redis_db.delete(user_id):
                    return {'status': '200'}
            else:
                return result_log
        else:
            raise UnauthorizedError('Token missing')


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError('Controller is none.')
    return controller
