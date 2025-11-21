from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "errors": {}, "success": None}
    )

@router.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...),
):
    repo = UserRepository(db)
    errors = {}

    # --- VALIDATION ---
    if len(username) < 2:
        errors["username"] = "Ім’я користувача повинно містити мінімум 2 символи"

    if len(password) < 6:
        errors["password"] = "Пароль має містити щонайменше 6 символів"

    if password != confirmPassword:
        errors["confirmPassword"] = "Паролі не співпадають"

    if repo.find_by_username(username):
        errors["username"] = "Користувач з таким логіном вже існує"

    if repo.find_by_email(email):
        errors["email"] = "Користувач з таким email вже існує"

    if errors:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "errors": errors,
                "success": None,
                "username": username,
                "email": email,
            }
        )

    user = User(
        username=username,
        email=email,
        password=password
    )
    repo.save(user)
    db.commit()

    request.session["success_register"] = "Реєстрація успішна! Тепер увійдіть у свій акаунт."

    return RedirectResponse("/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    message = request.session.pop("success_register", None)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "message": message}
    )


@router.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    repo = UserRepository(db)
    user = repo.find_by_username(username)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Користувача з таким логіном не існує", "message": None}
        )

    if user.password != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Невірний пароль", "message": None}
        )

    request.session["loggedUser"] = user.id
    request.session["username"] = user.username

    return RedirectResponse("/", status_code=302)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)