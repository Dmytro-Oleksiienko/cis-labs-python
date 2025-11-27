import os


class RabbitMQConfig:
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

    ORDERS_EXCHANGE = "orders.exchange"

    ORDERS_NEW_QUEUE = "orders.new.queue"
    ORDERS_NEW_ROUTING_KEY = "orders.new"

    ORDERS_CONFIRMED_QUEUE = "orders.confirmed.queue"
    ORDERS_CONFIRMED_ROUTING_KEY = "orders.confirmed"

    ORDERS_CANCELLED_QUEUE = "orders.cancelled.queue"
    ORDERS_CANCELLED_ROUTING_KEY = "orders.cancelled"