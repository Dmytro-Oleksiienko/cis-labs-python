from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.product_service import ProductService
from app.clients.bonus_client import BonusClient

router = APIRouter(prefix="/cart")
templates = Jinja2Templates(directory="app/templates")


def _get_cart_from_session(request: Request) -> List[dict]:
    cart = request.session.get("cart")
    if cart is None:
        cart = []
    return cart


def _save_cart_to_session(request: Request, cart: List[dict]) -> None:
    request.session["cart"] = cart


@router.get("", response_class=HTMLResponse)
def show_cart(request: Request):
    cart: List[dict] = _get_cart_from_session(request)

    total = sum(item["price"] * item["quantity"] for item in cart)
    count = sum(item["quantity"] for item in cart)

    bonus: int = 0
    if total > 0:
        try:
            client = BonusClient()
            bonus = client.calculate_bonus(total)
        except Exception as e:
            print(f"[Bonus] Не вдалося отримати бонус: {e}")
            bonus = 0

    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart": cart,
            "total": total,
            "count": count,
            "bonus": bonus,
            "user": getattr(request.state, "user", None),  # для хедера
        },
    )


@router.post("/add/{product_id}")
def add_to_cart(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.get_by_id(product_id)
    if not product:
        return RedirectResponse(url="/", status_code=302)

    cart: List[dict] = _get_cart_from_session(request)

    existing = next(
        (item for item in cart if item["product_id"] == product_id),
        None,
    )

    if existing:
        existing["quantity"] += 1
    else:
        cart.append(
            {
                "product_id": product.id,
                "name": product.name,
                "price": float(product.price or 0),
                "manufacturer": product.manufacturer,
                "country": product.country,
                "color": product.color,
                "image_url": product.image_url,
                "quantity": 1,
            }
        )

    _save_cart_to_session(request, cart)
    return RedirectResponse(url="/cart", status_code=302)

@router.post("/increase/{product_id}")
def increase(
    product_id: int,
    request: Request,
):
    cart: List[dict] = _get_cart_from_session(request)

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += 1
            break

    _save_cart_to_session(request, cart)
    return RedirectResponse(url="/cart", status_code=302)


@router.post("/decrease/{product_id}")
def decrease(
    product_id: int,
    request: Request,
):
    cart: List[dict] = _get_cart_from_session(request)
    new_cart: List[dict] = []

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] -= 1
            if item["quantity"] > 0:
                new_cart.append(item)
        else:
            new_cart.append(item)

    _save_cart_to_session(request, new_cart)
    return RedirectResponse(url="/cart", status_code=302)


@router.post("/checkout")
def checkout(request: Request):

    cart: List[dict] = _get_cart_from_session(request)
    if not cart:
        return RedirectResponse(url="/cart", status_code=302)

    return RedirectResponse(url="/cart/userinfo", status_code=302)

@router.get("/userinfo", response_class=HTMLResponse)
def userinfo(request: Request):
    username: Optional[str] = request.session.get("username")
    if not username:
        username = "Гість"

    return templates.TemplateResponse(
        "userinfo.html",
        {
            "request": request,
            "username": username,
            "user": getattr(request.state, "user", None),
        },
    )

