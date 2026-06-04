from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import os
import pika
from datetime import datetime
from .models import Order, OrderItem

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'

def publish_event(routing_key: str, payload: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30)
        )
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

def order_to_dict(order):
    items = []
    for item in order.items.all():
        items.append({
            'product_id': item.product_id,
            'quantity': item.quantity
        })
    
    return {
        'id': order.id,
        'tracking_id': order.tracking_id,
        'user_id': order.user_id,
        'full_name': order.full_name,
        'address': order.address,
        'phone': order.phone,
        'items': items,
        'total': order.total,
        'status': order.status,
        'created_at': order.created_at,
        'completed_at': order.completed_at
    }

@csrf_exempt
def order_list_or_create(request):
    if request.method == 'GET':
        orders = Order.objects.all().order_by('-id')
        return JsonResponse([order_to_dict(o) for o in orders], safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
        created_at = datetime.utcnow().isoformat()
        
        order = Order.objects.create(
            user_id=data.get('user_id'),
            full_name=data.get('full_name'),
            address=data.get('address'),
            phone=data.get('phone'),
            total=float(data.get('total', 0) or 0),
            status='PENDING',
            created_at=created_at
        )
        
        tracking_id = data.get('tracking_id') or f'ORD-{order.id + 1000}'
        order.tracking_id = tracking_id
        order.save()
        
        items_data = data.get('items', [])
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item.get('product_id') or item.get('id'),
                quantity=item.get('quantity', 1)
            )
            
        # Refetch order to include items
        payload = order_to_dict(order)
        publish_event('order.created', payload)
        
        return JsonResponse(payload, status=201)

@csrf_exempt
def order_detail_or_update(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
        
    if request.method == 'GET':
        return JsonResponse(order_to_dict(order))
        
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
        new_status = data.get('status')
        if not new_status:
            return JsonResponse({'error': 'Status is required'}, status=400)
            
        order.status = new_status
        if new_status in ['COMPLETED', 'DELIVERED']:
            order.completed_at = datetime.utcnow().isoformat()
        order.save()
        
        payload = order_to_dict(order)
        publish_event('order.updated', payload)
        
        return JsonResponse(payload)

def health(request):
    return JsonResponse({'service': 'order_service', 'status': 'ok'})
