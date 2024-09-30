import asyncio
from fastapi import Request
from src.models.work_to_jwt import jwt_work

class ProcessReque:

    def access_head(self, request: Request):
        if request.headers.get('authorization'):
            result = jwt_work.get_user_from_access(request.headers.get('authorization'))
            return result
        else:
            return {'error': 'Отсутствует токен.'}


    def refresh_head(self, request: Request):
        if request.headers.get('refresh'):
            result = jwt_work.get_user_from_refresh(request.headers.get('refresh'))
            return result
        else:
            return False


process_req = ProcessReque()