from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from .models import CartItem

def health(request):
    return JsonResponse({'service': 'cart_service', 'status': 'ok'})

def get_cart(request, user_id):
    items = CartItem.objects.filter(user_id=user_id).order_by('-id')
    cart_items = [{'product_id': item.product_id, 'quantity': item.quantity} for item in items]
    return JsonResponse({'user_id': user_id, 'items': cart_items})

@csrf_exempt
def add_item(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    user_id = int(data.get('user_id', 0))
    product_id = str(data.get('product_id', '')).strip()
    quantity = int(data.get('quantity', 1))

    if not user_id or not product_id:
        return JsonResponse({'error': 'user_id and product_id are required'}, status=400)
    if quantity <= 0:
        quantity = 1

    now = datetime.utcnow().isoformat()
    
    cart_item, created = CartItem.objects.get_or_create(
        user_id=user_id,
        product_id=product_id,
        defaults={'quantity': quantity, 'updated_at': now}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.updated_at = now
        cart_item.save()
        
    items = CartItem.objects.filter(user_id=user_id).order_by('-id')
    cart_items = [{'product_id': item.product_id, 'quantity': item.quantity} for item in items]
    return JsonResponse({'message': 'Item added', 'cart': cart_items})

@csrf_exempt
def remove_item(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    user_id = int(data.get('user_id', 0))
    product_id = str(data.get('product_id', '')).strip()

    if not user_id or not product_id:
        return JsonResponse({'error': 'user_id and product_id are required'}, status=400)

    CartItem.objects.filter(user_id=user_id, product_id=product_id).delete()
    
    items = CartItem.objects.filter(user_id=user_id).order_by('-id')
    cart_items = [{'product_id': item.product_id, 'quantity': item.quantity} for item in items]
    return JsonResponse({'message': 'Item removed', 'cart': cart_items})
