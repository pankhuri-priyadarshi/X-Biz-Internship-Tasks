import pika
import os
import shutil

def delete_folder(ch, method, properties, body):
    folder_path = body.decode()
    print(f"Received target to delete: {folder_path}")

    if os.path.exists(folder_path):
        try:
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")

            elif os.path.isfile(folder_path):
                os.remove(folder_path)
                print(f"Deleted file: {folder_path}")
                
            else:
                print(f"Unknown type (not file/folder): {folder_path}")
        except Exception as e:
            print(f"Error deleting {folder_path}: {e}")
    else:
        print(f"Path not found: {folder_path}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='delete_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='delete_queue', on_message_callback=delete_folder)

print("Waiting for folder/file names to delete... Press CTRL+C to exit.")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping consumer...")
    channel.close()
    connection.close()
