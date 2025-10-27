import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue # Gives a random queue name, exclusive=True makes sure the queue is deleted when the connection closes.

binding_keys = sys.argv[1:] or ['#']

for key in binding_keys:
    channel.queue_bind(
        exchange='topic_logs',
        queue=queue_name,
        routing_key=key
    )

print(f" [*] Waiting for logs: {binding_keys}")

def callback(ch, method, properties, body):
    print(f" [x] Received [{method.routing_key}]: {body.decode()}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)
try:
    print(' [*] To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    print('Interrupted')
    connection.close()
    channel.stop_consuming()
    sys.exit(0)
    
