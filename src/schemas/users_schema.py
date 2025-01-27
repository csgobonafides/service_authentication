from pydantic import BaseModel


class UserRequest(BaseModel):
    login: str
    password: str
    email: str


class UserReaponse(BaseModel):
    id: int
    login: str
    password: str
    email: str
    role: str
    date_of_registration: str
