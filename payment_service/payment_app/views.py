from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from .consumers import upsert_payment
import json

def health(request):
    return JsonResponse({'service': 'payment_service', 'status': 'ok'})

@csrf_exempt
def payment_list_or_create(request):
    if request.method == 'GET':
        payments = Payment.objects.all().order_by('-id')
        output = []
        for p in payments:
            output.append({
                'id': p.id,
                'order_id': p.order_id,
                'amount': p.amount,
                'method': p.method,
                'status': p.status,
                'created_at': p.created_at,
                'source': p.source
            })
        return JsonResponse(output, safe=False)
        
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
        order_id = int(data.get('order_id', 0))
        amount = float(data.get('amount', 0) or 0)
        method = data.get('method', 'COD')
        
        if not order_id:
            return JsonResponse({'error': 'order_id is required'}, status=400)

        payment_data = upsert_payment(order_id, amount, method, 'api')
        return JsonResponse(payment_data, status=201)

def get_payment_by_order(request, order_id):
    try:
        p = Payment.objects.get(order_id=order_id)
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
        
    return JsonResponse({
        'id': p.id,
        'order_id': p.order_id,
        'amount': p.amount,
        'method': p.method,
        'status': p.status,
        'created_at': p.created_at,
        'source': p.source
    })
