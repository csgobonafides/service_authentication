from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from time import monotonic
import logging

from core.settings import get_settings
from storages.redisstorage import RedisStorage
from api.routs import router
from db.connector import DatabaseConnector

import controllers.controler as c

config = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db = DatabaseConnector(config.DB.asyncpg_url)
    redis_db = RedisStorage()
    redis_db.connect()
    c.controller = c.Conntroller(db, redis_db)
    yield
    await redis_db.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def time_log_middleware(request: Request, call_next):
    start_time = monotonic()
    try:
        return await call_next(request)
    finally:
        finish_time =1000.0 * (monotonic() - start_time)
        process_time = "{:0.6f}|ms".format(finish_time)
        logger.info(f"Response: {request.url.path} Duration {process_time}")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
