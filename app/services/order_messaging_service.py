import pika
from app.config.rabbitmq_config import RabbitMQConfig

_connection = None
_channel = None


def get_rabbitmq_channel():
    global _connection, _channel

    if _channel and _channel.is_open:
        return _channel

    if _connection and _connection.is_open:
        _connection.close()

    params = pika.ConnectionParameters(
        host=RabbitMQConfig.RABBITMQ_HOST,
        port=RabbitMQConfig.RABBITMQ_PORT
    )
    _connection = pika.BlockingConnection(params)
    _channel = _connection.channel()

    _channel.exchange_declare(
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        exchange_type="topic",
        durable=True,
    )
    _channel.queue_declare(
        queue=RabbitMQConfig.ORDERS_NEW_QUEUE,
        durable=True,
    )
    _channel.queue_bind(
        queue=RabbitMQConfig.ORDERS_NEW_QUEUE,
        exchange=RabbitMQConfig.ORDERS_EXCHANGE,
        routing_key=RabbitMQConfig.ORDERS_NEW_ROUTING_KEY,
    )

    return _channel