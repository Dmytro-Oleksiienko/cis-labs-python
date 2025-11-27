import os
import time
import json
import threading
import pika
from pika.exceptions import AMQPConnectionError

from app.config.rabbitmq_config import RabbitMQConfig


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")


class OrderProcessingListener:

    def __init__(self):
        self.connection = None
        self.channel = None

        for attempt in range(5):
            try:
                print(
                    f"[OrderProcessingListener] Спроба підключення до RabbitMQ "
                    f"{RABBITMQ_HOST}, спроба {attempt + 1}/5"
                )

                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBITMQ_HOST)
                )
                self.channel = self.connection.channel()

                self.channel.queue_declare(
                    queue=RabbitMQConfig.ORDERS_NEW_QUEUE,
                    durable=True
                )

                print("[OrderProcessingListener] Підключення до RabbitMQ успішне")
                break

            except AMQPConnectionError as e:
                print(f"[OrderProcessingListener] Помилка підключення: {e}")
                self.connection = None
                self.channel = None
                time.sleep(3)

        if self.connection is None:
            print(
                "[OrderProcessingListener] ❗ Не вдалося підключитися до RabbitMQ, "
                "листенер буде вимкнений."
            )

    def start(self):
        if not self.channel:
            print(
                "[OrderProcessingListener] Немає каналу RabbitMQ, "
                "споживання повідомлень не запущено."
            )
            return

        print("🔄 Waiting for NEW orders...")

        self.channel.basic_consume(
            queue=RabbitMQConfig.ORDERS_NEW_QUEUE,
            on_message_callback=self.handle_order_created,
            auto_ack=True
        )

        t = threading.Thread(target=self.channel.start_consuming)
        t.daemon = True
        t.start()


    def handle_order_created(self, ch, method, properties, body):
        msg = body.decode("utf-8")

        try:
            payload = json.loads(msg)

            order_id = payload.get("ORDER_ID")
            user = payload.get("USER", "Guest")
            total = float(payload.get("TOTAL", 0.0))

            items = []
            for item in payload.get("ITEMS", []):
                name = item.get("productName")
                qty = item.get("quantity")
                price = item.get("price")
                items.append(f"{name} x{qty} @ {price} грн")

        except json.JSONDecodeError:
            map_data = self.parse_message(msg)

            order_id = map_data.get("ORDER_ID", "?")
            user = map_data.get("USER", "Guest")
            total = float(map_data.get("TOTAL", 0.0))
            items_raw = map_data.get("ITEMS", "[]").strip()

            items = self.parse_items(items_raw)

        self.print_order(order_id, user, total, items)
        choice = self.ask_choice()

        if choice == 1:
            self.handle_confirm(order_id, user, total, items)
        else:
            self.handle_cancel(order_id, user, total, items)

    def handle_confirm(self, order_id, user, total, items):
        base = self.base_payload(order_id, user, total, items)
        payload = f"CONFIRMED | {base}"

        self.channel.basic_publish(
            exchange=RabbitMQConfig.ORDERS_EXCHANGE,
            routing_key=RabbitMQConfig.ORDERS_CONFIRMED_ROUTING_KEY,
            body=payload.encode("utf-8")
        )

        print("✅ Замовлення підтверджено.")
        print("➡️ [CONFIRMED] Відправлено в канал підтверджених замовлень.\n")

    def handle_cancel(self, order_id, user, total, items):
        reason = input("Вкажіть причину скасування: ").strip()
        if not reason:
            reason = "Не вказано"

        lost = total
        base = self.base_payload(order_id, user, total, items)
        payload = f"CANCELLED | {base}; REASON={reason}; LOST={lost}"

        self.channel.basic_publish(
            exchange=RabbitMQConfig.ORDERS_EXCHANGE,
            routing_key=RabbitMQConfig.ORDERS_CANCELLED_ROUTING_KEY,
            body=payload.encode("utf-8")
        )

        print("❌ Замовлення скасовано.")
        print("➡️ [CANCELLED] Відправлено в службу якості.\n")


    def print_order(self, order_id, user, total, items):
        print("\n============================================")
        print("        НОВЕ ЗАМОВЛЕННЯ ДЛЯ ЗБИРАННЯ")
        print("============================================")
        print(f"Номер замовлення : {order_id}")
        print(f"Клієнт           : {user}")
        print(f"Загальна сума    : {total:.2f} грн")
        print("--------------------------------------------")
        print("Перелік товарів:")

        if not items:
            print("  (немає даних про товари)")
        else:
            for i, item in enumerate(items, start=1):
                print(f"  {i}. {item}")

        print("============================================")
        print("Що зробити із замовленням?")
        print("[1] Підтвердити")
        print("[2] Скасувати")

    def ask_choice(self):
        while True:
            val = input("Ваш вибір: ").strip()
            if val == "1":
                return 1
            if val == "2":
                return 2
            print("Введіть 1 або 2.")


    def parse_message(self, msg: str):
        pairs = [p.strip() for p in msg.split(";") if "=" in p]
        return dict(p.split("=", 1) for p in pairs)

    def parse_items(self, raw: str):
        raw = raw.strip()
        if raw.startswith("["):
            raw = raw[1:]
        if raw.endswith("]"):
            raw = raw[:-1]
        if not raw.strip():
            return []
        parts = raw.split("),")
        items = []
        for p in parts:
            p = p.strip()
            if not p.endswith(")"):
                p += ")"
            items.append(p)
        return items

    def base_payload(self, order_id, user, total, items):
        return (
            f"ORDER_ID={order_id}; "
            f"USER={user}; "
            f"TOTAL={total}; "
            f"ITEMS=[{', '.join(items)}]"
        )