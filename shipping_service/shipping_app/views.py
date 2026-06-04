from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Shipment
from .consumers import upsert_shipment
import json

def health(request):
    return JsonResponse({'service': 'shipping_service', 'status': 'ok'})

@csrf_exempt
def shipment_list_or_create(request):
    if request.method == 'GET':
        shipments = Shipment.objects.all().order_by('-id')
        output = []
        for s in shipments:
            output.append({
                'id': s.id,
                'order_id': s.order_id,
                'carrier': s.carrier,
                'status': s.status,
                'created_at': s.created_at,
                'delivered_at': s.delivered_at,
                'source': s.source
            })
        return JsonResponse(output, safe=False)
        
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
        order_id = int(data.get('order_id', 0))
        carrier = data.get('carrier', 'Standard Express')
        
        if not order_id:
            return JsonResponse({'error': 'order_id is required'}, status=400)

        shipment_data = upsert_shipment(order_id, carrier, 'api')
        return JsonResponse(shipment_data, status=201)

@csrf_exempt
def get_shipment_by_order(request, order_id):
    try:
        s = Shipment.objects.get(order_id=order_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': 'Shipment not found'}, status=404)
        
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status:
                s.status = new_status
                if new_status in ['SHIPPED', 'DELIVERED'] and not s.delivered_at:
                    from datetime import datetime
                    s.delivered_at = datetime.utcnow().isoformat()
                s.save()
                
                if new_status == 'SHIPPED':
                    from .consumers import schedule_delivery
                    schedule_delivery(order_id, 300)
        except Exception:
            pass
            
    return JsonResponse({
        'id': s.id,
        'order_id': s.order_id,
        'carrier': s.carrier,
        'status': s.status,
        'created_at': s.created_at,
        'delivered_at': s.delivered_at,
        'source': s.source
    })
