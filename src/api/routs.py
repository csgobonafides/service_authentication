from fastapi import APIRouter, Depends, Request, Response

from src.schemas.users_schema import User
from src.controllers.controler import get_controller

router = APIRouter()


@router.post('/registration')
async def registration(user: User, request: Request, controller = Depends(get_controller)) -> Response:
    return await controller.registr(user.login, user.password)


@router.post('/authentication')
async def authentication(user: User, request: Request, controller = Depends(get_controller)) -> Response:
    return await controller.authentication(user.login, user.password, request)


@router.get('/exit')
async def exit(request: Request, controller = Depends(get_controller)) -> Response:
    if await controller.access_head(request):
        return await controller.login_from_del(request)


@router.post('/examination')
async def examination(request: Request, controller = Depends(get_controller)):
    return await controller.access_head(request)


@router.post('/update_token')
async def update_token(reauest: Request, controller = Depends(get_controller)):
    return await controller.refresh_head(reauest)
