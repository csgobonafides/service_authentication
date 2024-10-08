import asyncio
from fastapi import Request
from src.models.work_to_jwt import jwt_work
from src.data.state_white_jwt import work_to_white
from src._exceptions.to_except import UnauthorizedError

class ProcessReque:

    def access_head(self, request: Request):
        if request.headers.get('authorization'):
            result = jwt_work.get_user_from_access(request.headers.get('authorization')[7:])
            return result
        else:
            raise UnauthorizedError('Token missing')
            # return {'error': 'Отсутствует токен.'}


    def refresh_head(self, request: Request):
        if request.headers.get('refresh'):
            result = jwt_work.get_user_from_refresh(request.headers.get('refresh'))
            return result
        else:
            return False

    def login_from_del(self, request):
        if request.headers.get('authorization'):
            result = jwt_work.loging(request.headers.get('authorization')[7:])
            if result != {'Error': 'ExpiredSignatureError'} and result != {'Error': 'InvalidTokenError'}:
                work_to_white.delet_tokens(result)
                return True
            else:
                return result
        else:
            raise UnauthorizedError('Token missing')
            # return {'error': 'Отсутствует токен.'}


process_req = ProcessReque()