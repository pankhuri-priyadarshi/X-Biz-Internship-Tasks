import pika
import os

MAIN_DIR = r"C:\Users\Pankhuri Priyadarshi\Desktop\xbiz-Projects\rabbitmq\dummy_data"   

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='delete_queue', durable=True)

for folder_name in os.listdir(MAIN_DIR):
    folder_path = os.path.join(MAIN_DIR, folder_name)
    if os.path.isdir(folder_path) or os.path.isfile(folder_path):
        channel.basic_publish(
            exchange='',
            routing_key='delete_queue',
            body=folder_path.encode(),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Sent folder name: {folder_path}")

connection.close()
print("All folder names sent to RabbitMQ queue!")
