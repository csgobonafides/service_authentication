from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, INT, func


class UserModel(DeclarativeBase):
    id = Column(INT, primary_key=True)
    login = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False, default="user guest")
    date_of_registration = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
