import pika

connection = pika.BlockingConnection(
    #pika.ConnectionParameters(host='192.168.58.2', port=32643)
    pika.ConnectionParameters(host='127.0.0.1', port=5672)
)
channel = connection.channel()
channel.queue_declare(queue='test_queue') 

def callback(ch, method, properties, body):
    print("Received:", body.decode())

channel.basic_consume(queue='test_queue', on_message_callback=callback, auto_ack=True)

print("Waiting for messages...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping...")
    channel.stop_consuming()
    connection.close()

