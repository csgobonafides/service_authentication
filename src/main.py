from fastapi import FastAPI
from contextlib import asynccontextmanager

from middleware.time_meddle import MyMiddle
from core.settings import get_settings
from storages.redisstorage import RedisStorage
from api.routs import router
from db.connector import DatabaseConnector

import controllers.controler as c

config = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db = DatabaseConnector(config.DB.asyncpg_url)
    redis_db = RedisStorage()
    redis_db.connect()
    c.controller = c.Conntroller(db, redis_db)
    yield
    await redis_db.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(MyMiddle)
app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
