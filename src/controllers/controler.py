import jwt
from datetime import timedelta, datetime, timezone
from src._exceptions.to_except import ForbiddenError, UnauthorizedError
from fastapi import Request
from src.storages.jsonfilestorage import JsonFileStorage

class Conntroller:
    SECRET_KEY = 'secretkey'
    ALGORITM = 'HS256'
    def __init__(self, user_db, black_jwt, white_jwt):
        self.user_db: JsonFileStorage = user_db
        self.black_jwt: JsonFileStorage = black_jwt
        self.white_jwt: JsonFileStorage = white_jwt

    async def registr(self, login: str, psw: str):
        await self.user_db.add(login, psw)
        await self.white_jwt.add(login, [])
        await self.black_jwt.add(login, [])
        return {'status': '200'}

    async def authentication(self, login: str, psw: str):
        if await self.user_db.get(login):
            if await self.user_db.get(login) == psw:
                return await self.creat_pair_jwt(login)
            else:
                return {'error': 'Пороль не верный'}
        else:
            return {'error': 'Пользователь с таким логином не зарегистрирован.'}

    async def creat_pair_jwt(self, login: str):
        access = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        refresh = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        tokens = [access]
        a = await self.white_jwt.get(login)
        result = tokens + a
        await self.white_jwt.update(login, result)
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
            if access not in await self.black_jwt.get(payload.get('login')):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')

    async def get_user_from_refresh(self, refresh):
        try:
            payload = jwt.decode(refresh, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.black_jwt.get(payload.get('login')) == [] or refresh not in await self.black_jwt.get(payload.get('login')):
                wt = await self.white_jwt.get(payload.get('login'))
                bl = await self.black_jwt.get(payload.get('login'))
                print(wt, bl)
                all = wt + bl
                alll = all.append(refresh)
                await self.black_jwt.update(payload.get('login'), all)
                await self.white_jwt.delete_value(payload.get('login'))
                return await self.creat_pair_jwt(payload.get('login'))
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')
        else:
            raise ForbiddenError('Token to Black List.')


    def access_head(self, request: Request):
        if request.headers.get('authorization'):
            result = self.get_user_from_access(request.headers.get('authorization')[7:])
            return result
        else:
            raise UnauthorizedError('Token missing')

    def refresh_head(self, request: Request):
        if request.headers.get('refresh'):
            result = self.get_user_from_refresh(request.headers.get('refresh'))
            return result
        else:
            raise UnauthorizedError('Token missing')

    async def login_from_del(self, request):
        if request.headers.get('authorization'):
            result_log = self.loging(request.headers.get('authorization')[7:])
            if result_log != {'Error': 'ExpiredSignatureError'} and result_log != {'Error': 'InvalidTokenError'}:
                wt = await self.white_jwt.get(result_log)
                bl = await self.black_jwt.get(result_log)
                all = wt + bl
                await self.black_jwt.update(result_log, all)
                await self.white_jwt.delete_value(result_log)
                return {'status': '200'}
            else:
                return result_log
        else:
            raise UnauthorizedError('Token missing')


controller = None

def get_controller():
    if controller is None:
        raise ValueError('Controller is none.')
    return controller



