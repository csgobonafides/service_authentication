import asyncio
import abc
import json
from typing import Any, Optional
from pydantic import BaseModel
from pathlib import Path
from fastapi import FastAPI, Request
from data.state_db import User, JsonFileStorage, Registration, BaseStorageDB
from data.state_jwt import JsonFileStorageJWT, State, BaseStorage
# from models.processing_request import process_req
from src.middle_ware.time_meddle import MyMiddle

app = FastAPI()
app.add_middleware(MyMiddle)

import src.controllers.controler as c

def init():
    dir = Path(__file__).parent.parent.parent
    db_path = dir /'db.json'
    state_db = JsonFileStorage(db_path)
    work_to_user = Registration(state_db)
    blt_path = dir /'black_token.json'
    state_blt = JsonFileStorageJWT(blt_path)
    work_to_blt = State(state_blt)
    c.controller = c.Conntroller(work_to_user, work_to_blt)


@app.post('/registration')
async def registration(user: User):
    return c.controller.set_user(user.login, user.password)


@app.post('/authentication')
async def authentication(user: User):
    return c.controller.authentication(user.login, user.password)


# @app.get('/exit')
# async def exit(request: Request):
#     if process_req.access_head(request):
#         return process_req.login_from_del(request)
#     else:
#         return process_req.access_head(request)
#
#
# @app.get('/examination')
# async def examination(request: Request):
#     return process_req.access_head(request)
#
#
# @app.post('/update_token')
# async def update_token(reauest: Request):
#     return process_req.refresh_head(reauest)





if __name__ == '__main__':
    import uvicorn
    init()
    uvicorn.run(app, host='127.0.0.1', port=8000)