import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello_durable', durable=True)

channel.basic_publish(exchange='',
                      routing_key='hello_durable',
                      body='Hello from durable message!',
                      properties=pika.BasicProperties(delivery_mode=2))  # make message persistent--message will not be lost if RabbitMQ crashes
                      

print("Message sent to RabbitMQ!")
connection.close()
