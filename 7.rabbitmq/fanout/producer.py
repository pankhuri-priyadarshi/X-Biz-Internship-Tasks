import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='broadcast_exchange', exchange_type='fanout')

message = "New product launch: SmartTask Manager Pro!"

channel.basic_publish(exchange='broadcast_exchange',
                       routing_key='', 
                       body=message)

print(f"Broadcast sent: {message}")
connection.close()

# Run on 3 different terminals--> 3 .py files
# To open rabbitmq dashboard , use cmd:
# docker run -d --name rabbitmq-server -p 5672:5672 -p 15672:15672 rabbitmq:3-management
# Then access it via browser at http://localhost:15672 (default guest/guest) or 
# click on the port created on docker container and after guest login we can see the rabbitmq dashboard


