from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, PurchaseHistory, Category
from . import models as product_models
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import json

def auto_complete_orders():
    threshold = timezone.now() - timedelta(seconds=30)
    pending_orders = PurchaseHistory.objects.filter(status='pending', purchased_at__lt=threshold)
    if pending_orders.exists():
        count = pending_orders.count()
        pending_orders.update(status='completed')
        print(f"✅ Auto-completed {count} AI history records.")

def serialize_product(p):
    data = {
        "id": p.id, 
        "name": p.name, 
        "brand": p.brand,
        "category_name": p.category.name if p.category else 'General', 
        "price": str(p.price),
        "stock": p.stock, 
        "image_url": p.image_url, 
        "description": p.description,
        "attributes": {}
    }
    # Map category name to related_name
    if p.category:
        cat_name = p.category.name.lower()
        if cat_name == 'books':
            cat_name = 'book' # Book model vs Books category
        rel_name = f"{cat_name}_details"
        if hasattr(p, rel_name):
            rel_obj = getattr(p, rel_name)
            if rel_obj:
                attrs = {}
                for f in rel_obj._meta.fields:
                    if f.name not in ['id', 'product']:
                        val = getattr(rel_obj, f.name)
                        if val is not None:
                            attrs[f.name] = val
                data["attributes"] = attrs
    return data

def product_list(request):
    auto_complete_orders()
    products = Product.objects.all()
    data = [serialize_product(p) for p in products]
    return JsonResponse(data, safe=False)

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cat_name = data.get('category', 'General')
            category, _ = Category.objects.get_or_create(name=cat_name)
            
            new_prod = Product.objects.create(
                name=data.get('name'),
                brand=data.get('brand', 'MegaBrand'),
                price=data.get('price'),
                stock=data.get('stock', 10),
                category=category,
                description=data.get('description', ''),
                image_url=data.get('image_url', 'https://images.unsplash.com/photo-1542491509-1f014912113a?q=80&w=1470&auto=format&fit=crop')
            )
            
            attrs = data.get('attributes', {}) or data.get('attrs', {})
            mapping = {
                'mobile': product_models.Mobile, 'computer': product_models.Computer, 
                'clothes': product_models.Clothes, 'shoes': product_models.Shoes, 
                'watches': product_models.Watches, 'cosmetics': product_models.Cosmetics,
                'furniture': product_models.Furniture, 'kitchenware': product_models.Kitchenware, 
                'books': product_models.Book, 'book': product_models.Book, 
                'sportswear': product_models.Sportswear, 'accessories': product_models.Accessories
            }
            
            model_class = mapping.get(cat_name.lower())
            if model_class:
                valid_fields = [f.name for f in model_class._meta.fields if f.name not in ['id', 'product']]
                model_attrs = {k: v for k, v in attrs.items() if k in valid_fields}
                model_class.objects.create(product=new_prod, **model_attrs)
                
            return JsonResponse({"id": new_prod.id, "status": "Product Created"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def delete_product(request, pk):
    if request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return JsonResponse({"status": "Product Deleted"}, status=204)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Not Found"}, status=404)
    return JsonResponse({"error": "Method Not Allowed"}, status=405)

@csrf_exempt
def update_product(request, pk):
    if request.method == 'PUT' or (request.method == 'POST'):
        try:
            data = json.loads(request.body)
            product = Product.objects.get(pk=pk)
            product.name = data.get('name', product.name)
            product.brand = data.get('brand', product.brand)
            product.price = data.get('price', product.price)
            product.stock = data.get('stock', product.stock)
            
            cat_name = data.get('category')
            if cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name)
                product.category = category
                
            product.description = data.get('description', product.description)
            product.image_url = data.get('image_url', product.image_url)
            product.save()
            
            attrs = data.get('attributes', {}) or data.get('attrs', {})
            if attrs:
                mapping = {
                    'mobile': product_models.Mobile, 'computer': product_models.Computer, 
                    'clothes': product_models.Clothes, 'shoes': product_models.Shoes, 
                    'watches': product_models.Watches, 'cosmetics': product_models.Cosmetics,
                    'furniture': product_models.Furniture, 'kitchenware': product_models.Kitchenware, 
                    'books': product_models.Book, 'book': product_models.Book, 
                    'sportswear': product_models.Sportswear, 'accessories': product_models.Accessories
                }
                
                # Delete existing specific record if any
                for k, v in mapping.items():
                    rel_name = f"{k}_details"
                    if hasattr(product, rel_name):
                        rel_obj = getattr(product, rel_name)
                        if rel_obj:
                            rel_obj.delete()
                
                # Create new specific record
                model_class = mapping.get(product.category.name.lower())
                if model_class:
                    valid_fields = [f.name for f in model_class._meta.fields if f.name not in ['id', 'product']]
                    model_attrs = {k: v for k, v in attrs.items() if k in valid_fields}
                    model_class.objects.create(product=product, **model_attrs)
                    
            return JsonResponse({"status": "Product Updated"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Not Found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Method Not Allowed"}, status=405)

@csrf_exempt
def record_purchase(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            items = data.get('items', [])
            for item in items:
                product = Product.objects.filter(name=item.get('name')).first()
                if product:
                    PurchaseHistory.objects.create(user_id=user_id, product=product, quantity=1, status='pending')
            return JsonResponse({"status": "Success"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def product_detail(request, pk):
    auto_complete_orders()
    try:
        product = Product.objects.get(pk=pk)
        return JsonResponse(serialize_product(product))
    except Product.DoesNotExist:
        return JsonResponse({"error": "Not Found"}, status=404)
