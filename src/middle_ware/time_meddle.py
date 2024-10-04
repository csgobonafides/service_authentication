import asyncio
from time import monotonic
from src.models.loggs import logger
from typing import Callable
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class MyMiddle(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = monotonic()
        response = await call_next(request)
        finish_time = monotonic() - start_time
        logger.info(f'запрос эндпоинту - {str(request.url)[22:]} - обработан за {finish_time}.')
        print(str(request.url))
        return response
