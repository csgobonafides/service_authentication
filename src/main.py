from pathlib import Path
from fastapi import FastAPI
from src.middle_ware.time_meddle import MyMiddle
from src.storages.jsonfilestorage import JsonFileStorage
from src.storages.redisstorage import RedisStorage
from contextlib import asynccontextmanager
from src.api.routs import router


import src.controllers.controler as c

@asynccontextmanager
async def lifespan(_app: FastAPI):
    dir = Path(__file__).parent.parent
    user_db = JsonFileStorage(dir /'db.json')
    redis_db = RedisStorage()
    await redis_db.connect()
    await user_db.connect()
    c.controller = c.Conntroller(user_db, redis_db)
    yield
    await user_db.disconnect()
    await redis_db.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(MyMiddle)
app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)