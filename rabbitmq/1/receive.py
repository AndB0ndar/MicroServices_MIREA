import pika
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        '51.250.26.59', 5672, '/', pika.PlainCredentials('guest', 'guest123')))
channel = connection.channel()
# create queue
queue_name = 'ikbo-06_bondar'
channel.queue_declare(queue=queue_name, durable=True)

def callback(ch, method, properties, body):
    print(f"\tReceived {body}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

