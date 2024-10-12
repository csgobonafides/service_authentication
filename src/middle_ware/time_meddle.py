import asyncio
from time import monotonic
from src.loggings.loggs import logger
from typing import Callable
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class MyMiddle(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = monotonic()
        response = await call_next(request)
        elapsed = 1000.0 * (monotonic() - start_time)
        finish_time = "{:0.6f}|ms".format(elapsed)
        logger.info(f'запрос эндпоинту - {str(request.url)[22:]} - обработан за {finish_time}.')
        return response