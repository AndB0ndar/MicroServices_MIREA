import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        '51.250.26.59', 5672, '/', pika.PlainCredentials('guest', 'guest123')))
channel = connection.channel()

# create exchange wiht type direct
exchange_name = 'ikbo-06_bondar_direct_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

# send message
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'ARBON'
channel.basic_publish(
    exchange=exchange_name, routing_key=severity, body=message)

print(f"Sent {severity}:{message}")
connection.close()

