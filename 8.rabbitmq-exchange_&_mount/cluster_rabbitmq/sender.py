import pika
import time

time.sleep(10)  # Wait for RabbitMQ server to start

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='127.0.0.1', port=5672)
    #pika.ConnectionParameters(host='192.168.58.2', port=32643)

)
channel = connection.channel()
channel.queue_declare(queue='test_queue')

channel.basic_publish(exchange='', routing_key='test_queue', body='Hello User!')
print("Message sent!")

connection.close()
