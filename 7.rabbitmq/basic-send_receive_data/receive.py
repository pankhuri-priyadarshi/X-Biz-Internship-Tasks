import pika

def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello_durable', durable=True)

channel.basic_consume(queue='hello_durable', on_message_callback=callback, auto_ack=True)

print("Waiting for messages... Press CTRL+C to exit")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping consumer...")
    channel.close()
    connection.close()


