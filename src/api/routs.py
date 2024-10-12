from fastapi import APIRouter, Depends, Request
from src.models.state_db import User
from src.controllers.controler import get_controller

router = APIRouter()

@router.post('/registration')
async def registration(user: User, controller = Depends(get_controller)):
    return controller.registr(user.login, user.password)


@router.post('/authentication')
async def authentication(user: User, controller = Depends(get_controller)):
    return controller.authentication(user.login, user.password)


@router.get('/exit')
async def exit(request: Request, controller = Depends(get_controller)):
    if controller.access_head(request):
        return controller.login_from_del(request)
    else:
        return controller.access_head(request)


@router.post('/examination')
async def examination(request: Request, controller = Depends(get_controller)):
    return controller.access_head(request)


@router.post('/update_token')
async def update_token(reauest: Request, controller = Depends(get_controller)):
    return controller.refresh_head(reauest)