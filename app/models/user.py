from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

from typing import ClassVar
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    confirm_password: str | None = None

    notify = Column(Boolean, default=False)

    def __init__(self, username: str, email: str, password: str,
                 confirm_password: str | None = None, notify: bool = False):
        self.username = username
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.notify = notify

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"