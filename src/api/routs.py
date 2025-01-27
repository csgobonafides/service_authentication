from fastapi import APIRouter, Depends, Request, status

from schemas.users_schema import UserRequest
from controllers.controler import get_controller

router = APIRouter()


@router.post('/registration', response_model=str, status_code=status.HTTP_201_CREATED)
async def registration(
        user: UserRequest,
        controller=Depends(get_controller)
) -> str:
    return await controller.registr(user.login, user.password)


@router.post('/authentication', response_model=dict, status_code=status.HTTP_200_OK)
async def authentication(
        user: UserRequest,
        request: Request,
        controller=Depends(get_controller)
) -> dict:
    return await controller.authentication(user.login, user.password, request)


@router.get('/exit', status_code=status.HTTP_204_NO_CONTENT)
async def exit(
        request: Request,
        controller=Depends(get_controller)
) -> None:
    if await controller.access_head(request):
        await controller.login_from_del(request)


@router.post('/examination', response_model=str, status_code=status.HTTP_200_OK)
async def examination(
        request: Request,
        controller=Depends(get_controller)
) -> str:
    return await controller.access_head(request)


@router.post('/update_token', response_model=dict, status_code=status.HTTP_200_OK)
async def update_token(
        request: Request,
        controller=Depends(get_controller)
) -> dict:
    return await controller.refresh_head(request)
