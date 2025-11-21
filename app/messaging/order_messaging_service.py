import json
from typing import List

from app.models.order import Order
from app.config.init_rabbitmq import get_rabbitmq_channel
from app.config.rabbitmq_config import RabbitMQConfig


class OrderMessagingService:
    @staticmethod
    def send_order_created(order: Order) -> None:

        if not order or not order.items:
            return

        username = order.username.strip() if order.username else "Guest"

        total = sum(
            [
                (item.price or 0) * (item.quantity or 0)
                for item in order.items
            ]
        )

        items_payload: List[dict] = []
        for item in order.items:
            items_payload.append(
                {
                    "productName": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                }
            )

        payload = {
            "ORDER_ID": order.id,
            "USER": username,
            "TOTAL": total,
            "ITEMS": items_payload,
        }

        body = json.dumps(payload, ensure_ascii=False)

        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange=RabbitMQConfig.ORDERS_EXCHANGE,
            routing_key=RabbitMQConfig.ORDERS_NEW_ROUTING_KEY,
            body=body.encode("utf-8"),
        )

        print(f"[NEW] Sent to orders.new.queue: {body}")