from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, user: User) -> User:
        existing = self.repo.find_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email вже використовується!"
            )

        existing = self.repo.find_by_username(user.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username вже використовується!"
            )

        return self.repo.save(user)

    def login(self, username: str, password: str) -> User:
        user = self.repo.find_by_username(username)

        if not user or user.password != password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний логін або пароль"
            )

        return user