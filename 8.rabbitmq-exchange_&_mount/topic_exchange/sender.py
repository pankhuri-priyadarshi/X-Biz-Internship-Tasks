import pika
import random

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_keys = [
    'order.created',
    'order.deleted',
    'order.updated.status',
    'order.updated.payment',
    'user.signup',
    'user.login',
    'user.logout.status',
    'system.error'
]

for key in routing_keys:
    message = f"Event: {key}"
    channel.basic_publish(
        exchange='topic_logs',
        routing_key=key,
        body=message
    )
    print(f" [x] Sent {key}: {message}")

connection.close()
