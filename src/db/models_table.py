from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, INT, func


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "user_model"

    id = Column(INT, primary_key=True)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    role = Column(String(50), nullable=False, default="user guest")
    date_of_registration = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"UserModel({self.id=}, {self.login=}, {self.password=}, {self.email=}, {self.role=})"
