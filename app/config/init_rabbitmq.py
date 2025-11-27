import os
import pika
from app.config.rabbitmq_config import RabbitMQConfig

_rabbit_connection = None
_rabbit_channel = None

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")


def init_rabbitmq():
    global _rabbit_connection, _rabbit_channel

    _rabbit_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    _rabbit_channel = _rabbit_connection.channel()

    _rabbit_channel.exchange_declare(
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        exchange_type="topic",
        durable=True,
    )

    _rabbit_channel.queue_declare(RabbitMQConfig.ORDERS_NEW_QUEUE, durable=True)
    _rabbit_channel.queue_declare(RabbitMQConfig.ORDERS_CONFIRMED_QUEUE, durable=True)
    _rabbit_channel.queue_declare(RabbitMQConfig.ORDERS_CANCELLED_QUEUE, durable=True)

    _rabbit_channel.queue_bind(
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        queue=RabbitMQConfig.ORDERS_NEW_QUEUE,
        routing_key=RabbitMQConfig.ORDERS_NEW_ROUTING_KEY,
    )

    _rabbit_channel.queue_bind(
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        queue=RabbitMQConfig.ORDERS_CONFIRMED_QUEUE,
        routing_key=RabbitMQConfig.ORDERS_CONFIRMED_ROUTING_KEY,
    )

    _rabbit_channel.queue_bind(
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        queue=RabbitMQConfig.ORDERS_CANCELLED_QUEUE,
        routing_key=RabbitMQConfig.ORDERS_CANCELLED_ROUTING_KEY,
    )

    print("RabbitMQ initialized ✔")