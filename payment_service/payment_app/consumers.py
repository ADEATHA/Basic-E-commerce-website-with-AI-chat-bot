import pika
import json
import os
from datetime import datetime

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'
QUEUE_NAME = 'payment_order_created'

def publish_event(routing_key: str, payload: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"RabbitMQ publish failed ({routing_key}): {e}")
        return False

def upsert_payment(order_id: int, amount: float, method: str, source: str):
    from .models import Payment
    created_at = datetime.utcnow().isoformat()
    
    payment, created = Payment.objects.get_or_create(
        order_id=order_id,
        defaults={
            'amount': amount,
            'method': method,
            'status': 'PAID',
            'created_at': created_at,
            'source': source
        }
    )
    if not created:
        payment.amount = amount
        payment.method = method
        payment.status = 'PAID'
        payment.source = source
        payment.save()

    payload = {
        'id': payment.id,
        'order_id': payment.order_id,
        'amount': payment.amount,
        'method': payment.method,
        'status': payment.status,
        'created_at': payment.created_at,
        'source': payment.source
    }
    publish_event('payment.success', payload)
    return payload

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='order.created')

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode('utf-8'))
                    order_id = int(payload.get('id'))
                    amount = float(payload.get('total', 0) or 0)
                    upsert_payment(order_id, amount, 'COD', 'event')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as cb_err:
                    print(f"payment consumer error: {cb_err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()
        except Exception as e:
            print(f"payment consumer reconnecting: {e}")
            import time
            time.sleep(5)
