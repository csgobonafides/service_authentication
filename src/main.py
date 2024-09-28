import asyncio
from fastapi import FastAPI, Request
from data.state_db import work_to_user, User

app = FastAPI()


@app.post('/registration')
async def registration(user: User):
    return work_to_user.set_user(user.login, user.password)


@app.post('/authentication')
async def authentication(user: User):
    pass




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)