import asyncio
from typing import Any, Optional
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from models.state_db import User, JsonFileStorage, Registration
from models.state_white_jwt import JsonFileStorageWJWT, StateWJWT
from models.state_jwt import JsonFileStorageJWT, StateJWT, BaseStorage
from src.middle_ware.time_meddle import MyMiddle
from contextlib import asynccontextmanager
from src.api.routs import router


import src.controllers.controler as c

@asynccontextmanager
async def lifespan(_app: FastAPI):
    dir = Path(__file__).parent.parent
    db_path = dir /'db.json'
    print(db_path)
    state_db = JsonFileStorage(db_path)
    work_to_user = Registration(state_db)
    state_white = JsonFileStorageWJWT(dir /'white_token.json')
    work_to_white = StateWJWT(state_white)
    state_blt = JsonFileStorageJWT(dir /'black_token.json')
    work_to_blt = StateJWT(state_blt)
    c.controller = c.Conntroller(work_to_user, work_to_blt, work_to_white)
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(MyMiddle)
app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)