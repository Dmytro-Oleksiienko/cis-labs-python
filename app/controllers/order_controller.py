from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.messaging.order_messaging_service import OrderMessagingService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/userinfo", response_class=HTMLResponse)
def user_info_form(request: Request):
    return templates.TemplateResponse(
        "userinfo.html",
        {
            "request": request,
            "order": {},
        },
    )


@router.post("/order/submit", response_class=HTMLResponse)
def submit_order(
    request: Request,
    address: str = Form(...),
    credit_card: str = Form(...),
    db: Session = Depends(get_db),
):
    session = request.session
    cart = session.get("cart")

    if not cart:
        return templates.TemplateResponse(
            "cart.html",
            {
                "request": request,
                "message": "Ваш кошик порожній",
            },
        )

    session_username: Optional[str] = session.get("username")
    if session_username and session_username.strip():
        username = session_username
    else:
        username = "Guest"

    order = Order(
        username=username,
        address=address,
        credit_card=credit_card,
    )

    db.add(order)
    db.flush()

    order_items: List[OrderItem] = []

    for item in cart:
        product_name = item.get("product_name") or item.get("name")
        price = float(item.get("price", 0))
        quantity = int(item.get("quantity", 1))

        order_item = OrderItem(
            order=order,
            product_name=product_name,
            price=price,
            quantity=quantity,
        )
        db.add(order_item)
        order_items.append(order_item)

    order.items = order_items

    db.commit()
    db.refresh(order)

    messaging = OrderMessagingService()
    messaging.send_order_created(order)

    session.pop("cart", None)

    return templates.TemplateResponse(
        "thankyou.html",
        {
            "request": request,
            "order": order,
        },
    )