import pika, time

def callback(ch, method, properties, body):
    print(f"Worker2 got: {body.decode()}")
    time.sleep(3)  
    print("Worker2 done!")
    ch.basic_ack(delivery_tag=method.delivery_tag) # require manual ack to ensure message is processed i.e ack is true.

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='task_queue', on_message_callback=callback)
print("Worker2 waiting for tasks...")
channel.start_consuming()
