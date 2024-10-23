import jwt
from datetime import timedelta, datetime, timezone
from src._exceptions.to_except import ForbiddenError, UnauthorizedError
from fastapi import Request
from src.storages.jsonfilestorage import JsonFileStorage
from src.storages.redisstorage import RedisStorage

class Conntroller:
    SECRET_KEY = 'secretkey'
    ALGORITM = 'HS256'
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
                return await self.creat_pair_jwt(login, data[0], us_ag)
            else:
                return {'error': 'Пороль не верный'}
        else:
            return {'error': 'Пользователь с таким логином не зарегистрирован.'}

    async def creat_pair_jwt(self, login: str, user_id: str, user_agent: str):
        access = jwt.encode({'login': login, 'id': id, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        refresh = jwt.encode({'login': login, 'id': id, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        await self.redis_db.add(user_id, access, refresh, user_agent)
        return {'access': access,
                'refresh': refresh}

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
            raise ValueError('Token missing')

    async def get_user_from_refresh(self, refresh, request: Request):
        try:
            payload = jwt.decode(refresh, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.redis_db.update():
                user_ag = request.headers.get('User-Agent')
                user_id = payload.get('id')
                return await self.creat_pair_jwt(payload.get('login'), user_id, user_ag)
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
        else:
            raise ForbiddenError('Token to Black List.')


    async def access_head(self, request: Request):
        if request.headers.get('authorization'):
            result = await self.get_user_from_access(request.headers.get('authorization')[7:], request)
            return result
        else:
            raise UnauthorizedError('Token missing')

    async def refresh_head(self, request: Request):
        if request.headers.get('refresh'):
            result = await self.get_user_from_refresh(request.headers.get('refresh'))
            return result
        else:
            raise UnauthorizedError('Token missing')

    async def login_from_del(self, request):
        if request.headers.get('authorization'):
            result_log = self.loging(request.headers.get('authorization')[7:])
            if result_log != {'Error': 'ExpiredSignatureError'} and result_log != {'Error': 'InvalidTokenError'}:
                payload = jwt.decode(request.headers.get('authorization')[7:], self.SECRET_KEY, algorithms=self.ALGORITM)
                user_id = payload.get('id')
                if await self.redis_db.delete(user_id):
                    return {'status': '200'}
                else:
                    raise ValueError("Что то не так")
            else:
                return result_log
        else:
            raise UnauthorizedError('Token missing')


controller = None

def get_controller():
    if controller is None:
        raise ValueError('Controller is none.')
    return controller



