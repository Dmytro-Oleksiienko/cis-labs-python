from typing import Optional, Dict

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "errors": {},
            "user": request.state.user,
            "form_user": None,
        },
    )


@router.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    errors: Dict[str, str] = {}

    # Валідація
    if len(username) < 2:
        errors["username"] = "Ім’я користувача повинно містити мінімум 2 символи"

    if len(password) < 6:
        errors["password"] = "Пароль має містити щонайменше 6 символів"

    if password != confirm_password:
        errors["confirm_password"] = "Паролі не співпадають"

    if UserRepository.find_by_username(db, username):
        errors["username"] = "Користувач з таким логіном вже існує"

    if UserRepository.find_by_email(db, email):
        errors["email"] = "Користувач з таким email вже існує"

    form_user = {
        "username": username,
        "email": email,
    }

    if errors:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "errors": errors,
                "user": request.state.user,
                "form_user": form_user,
            },
        )

    user = User(username=username, email=email, password=password)

    UserRepository.save(db, user)

    request.session["success_register"] = "Реєстрація успішна! Тепер увійдіть у свій акаунт."

    return RedirectResponse("/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    message: Optional[str] = request.session.pop("success_register", None)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
            "message": message,
            "user": request.state.user,
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    user = UserRepository.find_by_username(db, username)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Користувача з таким логіном не існує",
                "message": None,
                "user": request.state.user,
            },
        )

    if user.password != password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Невірний пароль",
                "message": None,
                "user": request.state.user,
            },
        )

    request.session["loggedUser"] = user.id
    request.session["username"] = user.username

    return RedirectResponse("/", status_code=302)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)