import datetime
from typing import Dict

import pika

from app.database.database import SessionLocal
from app.models.order_decision import OrderDecision
from app.repositories.order_decision_repo import OrderDecisionRepository
from app.config.rabbitmq_config import RabbitMQConfig


class ConfirmedOrdersListener:
    def __init__(self) -> None:
        # сесія БД для збереження рішень
        self.db = SessionLocal()
        self.decision_repo = OrderDecisionRepository(self.db)

    def start(self) -> None:

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        channel = connection.channel()

        channel.queue_declare(
            queue=RabbitMQConfig.ORDERS_CONFIRMED_QUEUE,
            durable=True
        )

        def callback(ch, method, properties, body):
            try:
                msg = body.decode("utf-8")
            except Exception:
                msg = str(body)

            print(f"[ConfirmedOrdersListener] Отримано повідомлення: {msg}")
            self.handle_confirmed(msg)

            # підтверджуємо, що повідомлення оброблено
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=RabbitMQConfig.ORDERS_CONFIRMED_QUEUE,
            on_message_callback=callback,
            auto_ack=False
        )

        print(
            f"[ConfirmedOrdersListener] Слухаю чергу "
            f"{RabbitMQConfig.ORDERS_CONFIRMED_QUEUE} ..."
        )
        try:
            channel.start_consuming()
        finally:
            connection.close()

    def handle_confirmed(self, msg: str) -> None:
        cleaned = msg.replace("CONFIRMED |", "").strip()
        data = self._parse(cleaned)

        order_id = self._parse_long(data.get("ORDER_ID"))
        username = data.get("USER", "Guest")
        total = self._parse_double(data.get("TOTAL"))

        decision = OrderDecision(
            order_id=order_id,
            username=username,
            status="CONFIRMED",
            total_amount=total,
            cancel_reason=None,
            lost_amount=0.0,
            created_at=datetime.datetime.now(),
        )

        self.decision_repo.save(decision)

        print(f"📦 [Закупівлі] Збережено підтверджене замовлення: {msg}")

    def _parse(self, msg: str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for part in msg.split(";"):
            part = part.strip()
            if "=" not in part:
                continue
            # важливо: maxsplit=1, щоб не зламатися, якщо в значенні буде '='
            key, value = part.split("=", 1)
            result[key] = value
        return result

    def _parse_long(self, v: str | None):
        try:
            return int(v.strip()) if v is not None else None
        except Exception:
            return None

    def _parse_double(self, v: str | None):
        try:
            return float(v.strip()) if v is not None else None
        except Exception:
            return None