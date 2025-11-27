import pika

from app.models.order import Order
from app.config.rabbitmq_config import RabbitMQConfig


class OrderMessagingService:
    @staticmethod
    def send_order_created(order: Order) -> None:

        if not order or not order.items:
            return

        username = order.username.strip() if order.username else "Guest"

        total = sum(
            (item.price or 0) * (item.quantity or 0)
            for item in order.items
        )

        items_strings = []
        for item in order.items:
            items_strings.append(f"{item.product_name} x{item.quantity} @ {item.price}")

        payload = (
            f"ORDER_ID={order.id}; "
            f"USER={username}; "
            f"TOTAL={total}; "
            f"ITEMS=[{', '.join(items_strings)}]"
        )

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RabbitMQConfig.RABBITMQ_HOST,
                port=RabbitMQConfig.RABBITMQ_PORT
            )
        )
        channel = connection.channel()

        channel.basic_publish(
            exchange=RabbitMQConfig.ORDERS_EXCHANGE,
            routing_key=RabbitMQConfig.ORDERS_NEW_ROUTING_KEY,
            body=payload.encode("utf-8"),
        )

        connection.close()

        print(f"[NEW] Sent: {payload}")