import pika

def callback(ch, method, properties, body):
    print(f"[Logger Service] recorded: {body.decode()}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='broadcast_exchange', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='broadcast_exchange', queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("[Logger Service] waiting for broadcast messages...")
channel.start_consuming()
