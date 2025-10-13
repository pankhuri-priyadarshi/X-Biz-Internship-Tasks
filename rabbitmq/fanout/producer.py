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


