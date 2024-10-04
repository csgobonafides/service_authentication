import asyncio
from fastapi import FastAPI, Request
from data.state_db import work_to_user, User
from models.auth_user import user_auth
from models.processing_request import process_req
from src.middle_ware.time_meddle import MyMiddle

app = FastAPI()
app.add_middleware(MyMiddle)

@app.post('/registration')
async def registration(user: User):
    return work_to_user.set_user(user.login, user.password)


@app.post('/authentication')
async def authentication(user: User):
    return user_auth.auth_user(user.login, user.password)


@app.get('/exit')
async def exit(request: Request):
    if process_req.access_head(request):
        return process_req.login_from_del(request)
    else:
        return process_req.access_head(request)


@app.get('/examination')
async def examination(request: Request):
    return process_req.access_head(request)


@app.post('/update_token')
async def update_token(reauest: Request):
    return process_req.refresh_head(reauest)





if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)