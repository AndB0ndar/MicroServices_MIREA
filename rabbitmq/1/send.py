import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        '51.250.26.59', 5672, '/', pika.PlainCredentials('guest', 'guest123')
        )
    )
channel = connection.channel()

# create queue
queue_name = 'ikbo-06_bondar'
# durable=True means that queue will be preserved when the server is restarted
channel.queue_declare(queue=queue_name, durable=True)

# send message
message = 'Yo, I am Bondar'
channel.basic_publish(
    exchange='', 
    routing_key=queue_name,
    body=message,
    properties=pika.BasicProperties(
        # make message persistent
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
print(f"Sent '{message}'")

connection.close()

