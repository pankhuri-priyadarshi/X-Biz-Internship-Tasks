import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='headers_logs', exchange_type='headers')

channel.queue_declare(queue='pdf_reports', durable=True)
channel.queue_declare(queue='images', durable=True)

channel.queue_bind(
    exchange='headers_logs',
    queue='pdf_reports',
    arguments={
        'x-match': 'all',
        'type': 'pdf',
        'format': 'report'
    }
)

channel.queue_bind(
    exchange='headers_logs',
    queue='images',
    arguments={
        'x-match': 'any',
        'type': 'image',
        'format': 'jpeg'
    }
)

def callback(ch, method, properties, body):
    print(f"[x] Received: {body.decode()} with headers {properties.headers}")

channel.basic_consume(queue='pdf_reports', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='images', on_message_callback=callback, auto_ack=True)

print("[*] Waiting for messages. To exit press CTRL+C")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    connection.close()
