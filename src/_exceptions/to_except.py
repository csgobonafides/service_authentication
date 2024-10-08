from fastapi import HTTPException
from starlette import status
from typing_extensions import Self


class BaseResponseError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self: Self, detail: str = None) -> None:
        super().__init__(status_code=self.status_code, detail=detail)

class UnauthorizedError(BaseResponseError):
    message_code = "unauthorized_error"
    status_code = status.HTTP_401_UNAUTHORIZED

class ForbiddenError(BaseResponseError):
    message_code = 'forbidden_error'
    status_code = status.HTTP_403_FORBIDDEN

class NotFoundError(BaseResponseError):
    message_code = 'not_found_error'
    status_code = status.HTTP_404_NOT_FOUND