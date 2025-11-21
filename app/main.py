import threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from app.controllers.auth_controller import router as auth_router
from app.controllers.cart_controller import router as cart_router
from app.controllers.order_controller import router as order_router
from app.controllers.order_decision_controller import router as order_decision_router
from app.controllers.product_controller import router as product_router
from app.controllers.web_product_controller import router as web_product_router

# Global exception handler
from app.exceptions.global_exception_handler import register_exception_handlers

# RabbitMQ init
from app.config.init_rabbitmq import init_rabbitmq

# Listeners
from app.messaging.order_processing_listener import OrderProcessingListener
from app.messaging.confirmed_orders_listener import ConfirmedOrdersListener
from app.messaging.cancelled_orders_listener import CancelledOrdersListener


# ------------------------------------------------------
#                   FASTAPI APP
# ------------------------------------------------------

app = FastAPI(title="CIS Labs Python Shop")


# ------------------------------------------------------
#                   ROUTERS
# ------------------------------------------------------

app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(order_decision_router)
app.include_router(product_router)
app.include_router(web_product_router)

register_exception_handlers(app)


# ------------------------------------------------------
#                   ROOT
# ------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Python shop is running on FastAPI 👍"}


# ------------------------------------------------------
#        BACKGROUND RABBITMQ LISTENER STARTER
# ------------------------------------------------------

def _start_listener(listener_obj, name: str) -> None:
    """
    Universal safe-thread starter for all RabbitMQ listeners
    """
    try:
        t = threading.Thread(target=listener_obj.start, name=name, daemon=True)
        t.start()
        print(f"✅ [{name}] started in background thread")
    except Exception as e:
        print(f"⚠️ Не вдалося запустити {name}: {e}")


# ------------------------------------------------------
#                STARTUP EVENT
# ------------------------------------------------------

@app.on_event("startup")
async def on_startup():

    # 1) Init RabbitMQ (exchange + queues + bindings)
    try:
        init_rabbitmq()
        print("✅ RabbitMQ infrastructure initialized")
    except Exception as e:
        print(f"⚠️ Помилка ініціалізації RabbitMQ: {e}")

    # 2) Start listeners
    _start_listener(OrderProcessingListener(), "OrderProcessingListener")
    _start_listener(ConfirmedOrdersListener(), "ConfirmedOrdersListener")
    _start_listener(CancelledOrdersListener(), "CancelledOrdersListener")

    print("🚀 All RabbitMQ listeners launched")