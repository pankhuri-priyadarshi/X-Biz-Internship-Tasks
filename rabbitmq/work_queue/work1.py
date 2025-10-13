import pika, time

def callback(ch, method, properties, body):
    print(f"Worker1 got: {body.decode()}")
    time.sleep(2)  
    print("Worker1 done!")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='task_queue', on_message_callback=callback)
print("Worker1 waiting for tasks...")
channel.start_consuming()
