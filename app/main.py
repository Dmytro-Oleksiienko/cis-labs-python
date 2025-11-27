import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

from app.controllers.auth_controller import router as auth_router
from app.controllers.cart_controller import router as cart_router
from app.controllers.order_controller import router as order_router
from app.controllers.order_decision_controller import router as order_decision_router
from app.controllers.product_controller import router as product_router
from app.controllers.web_product_controller import router as web_product_router
from app.exceptions.global_exception_handler import register_exception_handlers
from app.config.init_rabbitmq import init_rabbitmq
from app.messaging.order_processing_listener import OrderProcessingListener
from app.messaging.confirmed_orders_listener import ConfirmedOrdersListener
from app.messaging.cancelled_orders_listener import CancelledOrdersListener


def _start_listener(listener_obj, name: str) -> None:
    try:
        t = threading.Thread(target=listener_obj.start, name=name, daemon=True)
        t.start()
        print(f"✅ [{name}] started in background thread")
    except Exception as e:
        print(f"⚠️ Не вдалося запустити {name}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        init_rabbitmq()
        print("✅ RabbitMQ infrastructure initialized")
    except Exception as e:
        print(f"⚠️ Помилка ініціалізації RabbitMQ: {e}")

    _start_listener(OrderProcessingListener(), "OrderProcessingListener")
    _start_listener(ConfirmedOrdersListener(), "ConfirmedOrdersListener")
    _start_listener(CancelledOrdersListener(), "CancelledOrdersListener")
    print("🚀 All RabbitMQ listeners launched")

    yield

    print("🛑 FastAPI application shutdown, lifespan context exited")


app = FastAPI(title="CIS Labs Python Shop", lifespan=lifespan)


@app.middleware("http")
async def add_user_to_request(request: Request, call_next):

    user_data = None

    if "session" in request.scope:
        user_id = request.session.get("loggedUser")
        username = request.session.get("username")

        if user_id and username:
            user_data = {
                "id": user_id,
                "username": username,
            }

    request.state.user = user_data

    response = await call_next(request)
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY_123",
)


app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(order_decision_router)
app.include_router(product_router)
app.include_router(web_product_router)

register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}