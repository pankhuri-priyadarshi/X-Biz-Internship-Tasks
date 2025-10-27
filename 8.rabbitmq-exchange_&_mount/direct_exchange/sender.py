import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

messages = [
    ("info", "This is an info message"),
    ("error", "This is an error message"),
    ("warning", "This is a warning message")
]

for key, message in messages:
    channel.basic_publish(
        exchange='direct_logs',
        routing_key=key,           # important for direct exchange
        body=message
    )
    print(f" [x] Sent {key}: {message}")

connection.close()
