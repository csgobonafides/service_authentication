import jwt
from datetime import timedelta, datetime, timezone
from src._exceptions.to_except import ForbiddenError, UnauthorizedError
from fastapi import Request

class Conntroller:
    SECRET_KEY = 'secretkey'
    ALGORITM = 'HS256'
    def __init__(self, state1, state2, state3):
        self.user_db = state1
        self.blt_jwt = state2
        self.white_jwt = state3

    def registr(self, login: str, psw: str):
        return self.user_db.set_user(login, psw)

    def authentication(self, login: str, psw: str):
        if self.user_db.chek_user(login) == False:
            if self.user_db.check_psw(login, psw):
                return self.creat_pair_jwt(login)
            else:
                return {'error': 'Пороль не верный'}
        else:
            return {'error': 'Пользователь с таким логином не зарегистрирован.'}

    def creat_pair_jwt(self, login: str):
        access = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        refresh = jwt.encode({'login': login, 'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)}, self.SECRET_KEY, algorithm=self.ALGORITM)
        self.white_jwt.set_state(login, access)
        self.white_jwt.set_state(login, refresh)
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

    def get_user_from_access(self, access):
        try:
            payload = jwt.decode(access, self.SECRET_KEY, algorithms=self.ALGORITM)
            if payload.get('login'):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError')

    def get_user_from_refresh(self, refresh):
        try:
            payload = jwt.decode(refresh, self.SECRET_KEY, algorithms=self.ALGORITM)
            if self.blt_jwt.get_state(refresh, payload.get('login')):
                    self.blt_jwt.set_state(payload.get('login'), refresh)
                    return self.creat_pair_jwt(payload.get('login'))
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

    def login_from_del(self, request):
        if request.headers.get('authorization'):
            result_log = self.loging(request.headers.get('authorization')[7:])
            if result_log != {'Error': 'ExpiredSignatureError'} and result_log != {'Error': 'InvalidTokenError'}:
                list_tokens = self.white_jwt.delet_tokens(result_log)
                self.blt_jwt.set_state(result_log, list_tokens)
                return True
            else:
                return result_log
        else:
            raise UnauthorizedError('Token missing')


controller = None

def get_controller():
    if controller is None:
        raise ValueError('Controller is none.')
    return controller



