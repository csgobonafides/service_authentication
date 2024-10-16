import asyncio
from typing import Any, Optional
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from src.middle_ware.time_meddle import MyMiddle
from src.models.base import JsonFileStorage
from contextlib import asynccontextmanager
from src.api.routs import router


import src.controllers.controler as c

@asynccontextmanager
async def lifespan(_app: FastAPI):
    dir = Path(__file__).parent.parent
    user_db = JsonFileStorage(dir /'db.json')
    black_jwt = JsonFileStorage(dir /'black_token.json')
    white_jwt = JsonFileStorage(dir /'white_token.json')
    await user_db.connect()
    await black_jwt.connect()
    await white_jwt.connect()
    c.controller = c.Conntroller(user_db, black_jwt, white_jwt)
    yield
    await user_db.disconnect()
    await black_jwt.disconnect()
    await white_jwt.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(MyMiddle)
app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)