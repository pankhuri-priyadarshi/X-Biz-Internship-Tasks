import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)  # default exchange -- msg stored in given queue name(task_queue here)

for i in range(1, 11):
    message = f"Task number {i}"
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )
    print(f"Sent: {message}")
    time.sleep(0.3)

print("All tasks sent!")
connection.close()
