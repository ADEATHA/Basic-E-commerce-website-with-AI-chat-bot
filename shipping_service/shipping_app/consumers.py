import pika
import json
import os
from datetime import datetime
from threading import Timer

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'
QUEUE_NAME = 'shipping_payment_success'

def mark_shipment_delivered(order_id: int):
    from .models import Shipment
    import urllib.request
    import json
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        if shipment.status in ['PREPARING', 'SHIPPED']:
            shipment.status = 'DELIVERED'
            shipment.delivered_at = datetime.utcnow().isoformat()
            shipment.save()
            
            try:
                url = f'http://order:8000/{order_id}/'
                data = json.dumps({'status': 'DELIVERED'}).encode('utf-8')
                req = urllib.request.Request(url=url, data=data, method='PUT')
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=5) as response:
                    pass
            except Exception:
                pass
    except Shipment.DoesNotExist:
        pass

def schedule_delivery(order_id: int, delay_seconds: int = 60):
    timer = Timer(delay_seconds, mark_shipment_delivered, args=[order_id])
    timer.daemon = True
    timer.start()

def upsert_shipment(order_id: int, carrier: str, source: str):
    from .models import Shipment
    created_at = datetime.utcnow().isoformat()
    
    shipment, created = Shipment.objects.get_or_create(
        order_id=order_id,
        defaults={
            'carrier': carrier,
            'status': 'PREPARING',
            'created_at': created_at,
            'source': source
        }
    )
    if not created:
        shipment.carrier = carrier
        shipment.source = source
        shipment.save()
        
    if shipment.status == 'PREPARING':
        schedule_delivery(order_id, 60)

    return {
        'id': shipment.id,
        'order_id': shipment.order_id,
        'carrier': shipment.carrier,
        'status': shipment.status,
        'created_at': shipment.created_at,
        'delivered_at': shipment.delivered_at,
        'source': shipment.source
    }

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='payment.success')

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode('utf-8'))
                    order_id = int(payload.get('order_id'))
                    upsert_shipment(order_id, 'Standard Express', 'event')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as cb_err:
                    print(f"shipping consumer error: {cb_err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()
        except Exception as e:
            print(f"shipping consumer reconnecting: {e}")
            import time
            time.sleep(5)
