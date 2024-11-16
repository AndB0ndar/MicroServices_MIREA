import pika
import sys
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        '51.250.26.59', 5672, '/', pika.PlainCredentials('guest', 'guest123')))
channel = connection.channel()

# create exchange wiht type direct
exchange_name = 'ikbo-06_bondar_direct_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

queue = channel.queue_declare(queue='', exclusive=True)
queue_name = queue.method.queue

severities = sys.argv[1:]
if not severities:
    sys.exit(1)
for severity in severities:
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=severity)

def callback(ch, method, properties, body):
    task = body.decode()
    print(f"\tReceived {task}")
    sleep_time = task.count('*')
    time.sleep(sleep_time)  # Задержка на время, равное количеству символов '*'
    print(f"\tDone, slept for {sleep_time} seconds")
    ch.basic_ack(method.delivery_tag)

print('Waiting for logs. To exit press CTRL+C')
channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()

