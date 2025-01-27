import jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from core.loggs_controll import logger_controll
from core.exceptions import ForbiddenError, UnauthorizedError, NotFoundError

from db.connector import DatabaseConnector
from db.models_table import UserModel
from storages.redisstorage import RedisStorage

load_dotenv()


class Conntroller:
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITM = os.getenv('ALGORITM')

    def __init__(self, user_db, redis_db):
        self.user_db: DatabaseConnector = user_db
        self.redis_db: RedisStorage = redis_db

    async def registr(self, login: str, psw: str) -> str:
        logger_controll.info(f"User registration: {login}")

        async with self.user_db.session_maker() as session:
            try:
                user = UserModel(login=login, password=psw, role="user")
                session.add(user)
                await session.commit()
            except IntegrityError:
                logger_controll.error(f"Trying to add an existing user: {login}.")
                raise f"Trying to add an existing user: {login}."
        return f"{login} successfully registered."

    async def authentication(self, login: str, psw: str, request: Request) -> dict:
        logger_controll.info(f"User authentication: {login}")

        async with self.user_db.session_maker() as session:
            query = select(UserModel.id, UserModel.login, UserModel.password).where(UserModel.login == login)
            result = await session.execute(query)
            user = result.fetchone()
            if not user:
                logger_controll.error(f"User {login} not found.")
                raise UnauthorizedError('User not found.')
            elif user and user.password == psw:
                user_agent = request.headers.get('User-Agent')
                pair_jwt = await self.creat_pair_jwt(login, user.id)
                if await self.redis_db.add(user.id, pair_jwt[0], pair_jwt[1], user_agent):
                    return {'access': pair_jwt[0], 'refresh': pair_jwt[1]}
            else:
                logger_controll.error(f"{login}: The password is incorrect.")
                raise UnauthorizedError('The password is incorrect.')

    async def creat_pair_jwt(self, login: str, user_id: str) -> list:
        logger_controll.info(f"a pair of tokens has been created for the user: {login}")

        access = jwt.encode(
            {
                'login': login,
                'id': user_id,
                'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=1)
            },
            self.SECRET_KEY,
            algorithm=self.ALGORITM
        )
        refresh = jwt.encode(
            {
                'login': login,
                'id': user_id,
                'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10)
            },
            self.SECRET_KEY,
            algorithm=self.ALGORITM
        )
        return [access, refresh]

    def loging(self, access) -> str:
        try:
            payload = jwt.decode(access, self.SECRET_KEY, algorithms=self.ALGORITM)
            if payload.get('login'):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError.')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError.')

    async def get_user_from_access(self, access) -> str:
        try:
            payload = jwt.decode(access, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.redis_db.get(access):
                return payload.get('login')
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError.')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError.')
        else:
            raise NotFoundError('Token missing.')

    async def get_user_from_refresh(self, refresh, request: Request) -> dict:
        try:
            payload = jwt.decode(refresh, self.SECRET_KEY, algorithms=self.ALGORITM)
            if await self.redis_db.get(refresh):
                user_ag = request.headers.get('User-Agent')
                user_id = payload.get('id')
                result = await self.creat_pair_jwt(payload.get('login'), user_id)
                if await self.redis_db.update(user_id, result[0], result[1], user_ag):
                    return {'access': result[0], 'refresh': result[1]}
        except jwt.ExpiredSignatureError:
            raise ForbiddenError('ExpiredSignatureError.')
        except jwt.InvalidTokenError:
            raise ForbiddenError('InvalidTokenError.')
        else:
            raise ForbiddenError('Token is blacklisted.')

    async def access_head(self, request: Request) -> str:
        if request.headers.get('authorization'):
            result = await self.get_user_from_access(request.headers.get('authorization')[7:])
            return result
        else:
            raise NotFoundError('Token missing.')

    async def refresh_head(self, request: Request) -> dict:
        if request.headers.get('refresh'):
            result = await self.get_user_from_refresh(request.headers.get('refresh'), request)
            return result
        else:
            raise NotFoundError('Token missing.')

    async def login_from_del(self, request) -> None:
        if request.headers.get('authorization'):
            payload = jwt.decode(request.headers.get('authorization')[7:], self.SECRET_KEY, algorithms=self.ALGORITM)
            user_id = payload.get('id')
            if await self.redis_db.delete(user_id):
                logger_controll.info(f"{payload.get('login')} User tokens have been removed.")
        else:
            raise UnauthorizedError('Token missing.')


controller = None


def get_controller():
    if controller is None:
        raise ForbiddenError('Controller is none.')
    return controller
