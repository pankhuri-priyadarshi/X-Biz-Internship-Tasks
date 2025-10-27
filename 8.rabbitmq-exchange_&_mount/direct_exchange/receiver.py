import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:] or ['info']  # used for giving list of command-line arguments
                                        # Take the keys (like error, warning) from the command line;-- python receiver.py error warning
                                        # if the user doesn’t give any, use ['info'] by default.

for severity in severities:
    channel.queue_bind(
        exchange='direct_logs',
        queue=queue_name,
        routing_key=severity  # bind to specific routing keys (different from fanout)
    )

print(f" [*] Waiting for logs: {severities}")

def callback(ch, method, properties, body):
    print(f" [x] Received {method.routing_key}: {body.decode()}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)
try:
    print(' [*] To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    print('Interrupted')
    channel.stop_consuming()
    connection.close()
    sys.exit(0)