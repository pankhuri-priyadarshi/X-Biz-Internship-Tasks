import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='headers_logs', exchange_type='headers')

messages = [
    ("PDF Report", {'type': 'pdf', 'format': 'report'}),
    ("Image Upload", {'type': 'image', 'format': 'jpeg'}),
    ("CSV Export", {'type': 'csv', 'format': 'data'})
]

for body, headers in messages:
    channel.basic_publish(
        exchange='headers_logs',
        routing_key='',
        body=body,
        properties=pika.BasicProperties(headers=headers)
    )
    print(f"[x] Sent: {body} with headers {headers}")

connection.close()
