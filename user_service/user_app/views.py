from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order
import requests
import json
import os

GATEWAY_BASE = os.getenv('GATEWAY_BASE', 'http://localhost:8100')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop')
    else:
        form = UserCreationForm()
    return render(request, 'customer/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('shop')
    else:
        form = AuthenticationForm()
    return render(request, 'customer/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('shop')


def shop(request):
    try:
        try:
            products = requests.get(f'{GATEWAY_BASE}/products/', timeout=8).json()
        except Exception:
            products = requests.get(f'{GATEWAY_BASE}/api/product/products/', timeout=8).json()
        categories = {}
        for p in products:
            cat = p.get('category_name', 'Other').title()
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(p)
    except Exception as e:
        print(f"Error fetching products: {e}")
        categories = {}

    return render(request, 'customer/shop.html', {
        'categories': categories
    })


def cart_view(request):
    return render(request, 'customer/cart.html')


@login_required(login_url='login')
def checkout(request):
    if request.method != 'POST':
        return redirect('cart')

    items_json = request.POST.get('items_json', '[]')
    total = request.POST.get('total_price', '0')
    full_name = request.POST.get('full_name')
    address = request.POST.get('address')
    phone = request.POST.get('phone')

    try:
        items = json.loads(items_json)
    except Exception:
        items = []

    try:
        # 1) Create order
        order_payload = {
            'user_id': request.user.id,
            'full_name': full_name,
            'address': address,
            'phone': phone,
            'items': items,
            'total': float(total or 0),
        }
        order_resp = requests.post(f'{GATEWAY_BASE}/orders/', json=order_payload, timeout=8)
        if not order_resp.ok:
            order_resp = requests.post(f'{GATEWAY_BASE}/api/order/orders', json=order_payload, timeout=8)
        order_resp.raise_for_status()
        order = order_resp.json()

        # 2) Create payment
        payment_payload = {
            'order_id': order['id'],
            'amount': order.get('total', 0),
            'method': 'COD'
        }
        pay_resp = requests.post(f'{GATEWAY_BASE}/payments/', json=payment_payload, timeout=8)
        if not pay_resp.ok:
            requests.post(f'{GATEWAY_BASE}/payments', json=payment_payload, timeout=8)

        # 3) Create shipment
        shipment_payload = {
            'order_id': order['id'],
            'carrier': 'Standard Express'
        }
        ship_resp = requests.post(f'{GATEWAY_BASE}/shipping/', json=shipment_payload, timeout=8)
        if not ship_resp.ok:
            requests.post(f'{GATEWAY_BASE}/shipping', json=shipment_payload, timeout=8)

        # 4) Sync to AI via product service
        try:
            try:
                requests.post(f'{GATEWAY_BASE}/products/record-purchase/', json={
                    'user_id': request.user.id,
                    'items': items
                }, timeout=5)
            except Exception:
                requests.post(f'{GATEWAY_BASE}/api/product/record-purchase/', json={
                    'user_id': request.user.id,
                    'items': items
                }, timeout=5)
        except Exception as ai_e:
            print(f"AI Sync error: {ai_e}")

        success_order = {
            'tracking_id': order.get('tracking_id', f"ORD-{order.get('id', '')}"),
            'total_price': order.get('total', 0),
            'full_name': order.get('full_name') or full_name,
            'id': order.get('id')
        }

        # Persist local snapshot for resilient tracking UI (survives microservice in-memory resets)
        try:
            Order.objects.update_or_create(
                tracking_id=success_order['tracking_id'],
                defaults={
                    'user': request.user,
                    'full_name': success_order['full_name'],
                    'address': order.get('address') or address,
                    'phone': order.get('phone') or phone,
                    'items_json': json.dumps(order.get('items', items)),
                    'total_price': order.get('total', total),
                    'status': order.get('status', 'Pending')
                }
            )
        except Exception as persist_e:
            print(f"Local snapshot persist error: {persist_e}")

        return render(request, 'customer/success.html', {'order': success_order})

    except Exception as e:
        # Legacy fallback for stability
        try:
            fallback_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                address=address,
                phone=phone,
                items_json=items_json,
                total_price=total
            )
            messages.warning(request, 'Microservice đang bận, hệ thống đã lưu đơn theo chế độ dự phòng.')
            return render(request, 'customer/success.html', {'order': fallback_order})
        except Exception:
            messages.error(request, f"Checkout failed: {e}")
            return redirect('cart')


def tracking(request):
    order = None
    order_items = []
    payment = None
    shipment = None

    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        if tracking_id and tracking_id.startswith('ORD-'):
            request.GET = request.GET.copy()
            request.GET['tid'] = tracking_id

    tracking_id = request.GET.get('tid')
    order_id = request.GET.get('order_id')

    # 1) Prefer microservice tracking by order_id
    if order_id:
        try:
            order_resp = requests.get(f'{GATEWAY_BASE}/orders/{order_id}/', timeout=6)
            if not order_resp.ok:
                order_resp = requests.get(f'{GATEWAY_BASE}/orders/{order_id}', timeout=6)
            if not order_resp.ok:
                order_resp = requests.get(f'{GATEWAY_BASE}/api/order/orders/{order_id}', timeout=6)
            if order_resp.ok:
                order = order_resp.json()
                order_items = order.get('items', [])

                pay_resp = requests.get(f'{GATEWAY_BASE}/payments/order/{order_id}/', timeout=5)
                if not pay_resp.ok:
                    pay_resp = requests.get(f'{GATEWAY_BASE}/api/payment/payments/order/{order_id}/', timeout=5)
                if pay_resp.ok:
                    payment = pay_resp.json()

                ship_resp = requests.get(f'{GATEWAY_BASE}/shipping/order/{order_id}/', timeout=5)
                if not ship_resp.ok:
                    ship_resp = requests.get(f'{GATEWAY_BASE}/api/shipping/shipments/order/{order_id}/', timeout=5)
                if ship_resp.ok:
                    shipment = ship_resp.json()
        except Exception:
            pass

    # 2) If only tracking_id, attempt to find in microservice list
    if not order and tracking_id:
        try:
            orders_resp = requests.get(f'{GATEWAY_BASE}/orders/', timeout=6)
            if not orders_resp.ok:
                orders_resp = requests.get(f'{GATEWAY_BASE}/api/order/orders', timeout=6)
            if orders_resp.ok:
                ms_orders = orders_resp.json()
                order = next((o for o in ms_orders if o.get('tracking_id') == tracking_id), None)
                if order:
                    order_items = order.get('items', [])
                    oid = order.get('id')
                    if oid:
                        pay_resp = requests.get(f'{GATEWAY_BASE}/payments/order/{oid}/', timeout=5)
                        if not pay_resp.ok:
                            pay_resp = requests.get(f'{GATEWAY_BASE}/api/payment/payments/order/{oid}/', timeout=5)
                        if pay_resp.ok:
                            payment = pay_resp.json()
                            
                        ship_resp = requests.get(f'{GATEWAY_BASE}/shipping/order/{oid}/', timeout=5)
                        if not ship_resp.ok:
                            ship_resp = requests.get(f'{GATEWAY_BASE}/api/shipping/shipments/order/{oid}/', timeout=5)
                        if ship_resp.ok:
                            shipment = ship_resp.json()
        except Exception:
            pass

    # 3) Build order history (prefer microservice, fallback DB)
    user_orders = []
    if request.user.is_authenticated:
        try:
            orders_resp = requests.get(f'{GATEWAY_BASE}/orders/', timeout=6)
            if not orders_resp.ok:
                # Attempt with legacy structure but same root
                orders_resp = requests.get(f'{GATEWAY_BASE}/orders', timeout=6)
            if orders_resp.ok:
                ms_orders = orders_resp.json() or []
                my_orders = [o for o in ms_orders if int(o.get('user_id', -1)) == request.user.id]
                my_orders.sort(key=lambda o: o.get('created_at', ''), reverse=True)
                user_orders = [
                    {
                        'tracking_id': o.get('tracking_id', f"ORD-{o.get('id', '')}"),
                        'created_at': o.get('created_at'),
                        'total_price': o.get('total', 0),
                        'status': o.get('status', 'PENDING')
                    }
                    for o in my_orders
                ]
        except Exception:
            user_orders = []

        if not user_orders:
            user_orders = list(Order.objects.filter(user=request.user).order_by('-created_at'))

    if not order and tracking_id:
        try:
            db_order = Order.objects.get(tracking_id=tracking_id)
            order = {
                'tracking_id': db_order.tracking_id,
                'full_name': db_order.full_name,
                'status': db_order.status,
                'created_at': db_order.created_at,
                'total_price': db_order.total_price,
            }
            try:
                order_items = json.loads(db_order.items_json or '[]')
            except Exception:
                order_items = []
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')

    # Populating missing product details for microservice items
    if order_items:
        resolved_items = []
        all_products = []
        try:
            p_all_resp = requests.get(f'{GATEWAY_BASE}/products/', timeout=4)
            if p_all_resp.ok:
                all_products = p_all_resp.json()
        except Exception:
            pass

        for item in order_items:
            pid = item.get('product_id') or item.get('id')
            if not item.get('name'):
                if pid:
                    try:
                        p_resp = requests.get(f'{GATEWAY_BASE}/products/{pid}/', timeout=3)
                        if p_resp.ok:
                            p_data = p_resp.json()
                            item['name'] = p_data.get('name')
                            item['brand'] = p_data.get('brand')
                            item['price'] = p_data.get('price')
                    except Exception:
                        pass
                
                if not item.get('name') and all_products:
                    for prod in all_products:
                        if str(prod.get('id')) == str(pid):
                            item['name'] = prod.get('name')
                            item['brand'] = prod.get('brand')
                            item['price'] = prod.get('price')
                            break
            resolved_items.append(item)
        order_items = resolved_items

    return render(request, 'customer/tracking.html', {
        'order': order,
        'order_items': order_items,
        'payment': payment,
        'shipment': shipment,
        'user_orders': user_orders
    })


# ---- STAFF VIEWS ----

def staff_register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True # Mandatory for staff accounts
            user.save()
            login(request, user)
            messages.success(request, 'Staff registration successful.')
            return redirect('staff_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'staff/register.html', {'form': form})

def staff_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect('staff_dashboard')
                else:
                    messages.error(request, 'This account is not a staff account.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'staff/login.html', {'form': form})

def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')

@login_required(login_url='staff_login')
def staff_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('staff_login')
    
    # Fetch from both Order Microservice and Local DB to prevent data gaps
    orders = []
    
    # 1) Pull from microservice
    try:
        ms_resp = requests.get(f'{GATEWAY_BASE}/orders/', timeout=6)
        if ms_resp.ok:
            ms_orders = ms_resp.json()
            for o in ms_orders:
                orders.append({
                    'id': o.get('id'),
                    'tracking_id': o.get('tracking_id'),
                    'full_name': o.get('full_name'),
                    'phone': o.get('phone'),
                    'total_price': o.get('total'),
                    'status': o.get('status', 'Pending').capitalize(), # Standardize capitalization for template logic
                    'created_at': o.get('created_at'),
                })
    except Exception as e:
        print(f"Microservice orders fetch failed: {e}")

    # 2) Merge with local snapshot fallback orders
    local_orders = Order.objects.all().order_by('-id')
    ms_tracking_ids = {o['tracking_id'] for o in orders if o.get('tracking_id')}
    
    for lo in local_orders:
        if lo.tracking_id not in ms_tracking_ids:
            orders.append({
                'id': lo.id,
                'tracking_id': lo.tracking_id,
                'full_name': lo.full_name,
                'phone': lo.phone,
                'total_price': lo.total_price,
                'status': lo.status,
                'created_at': lo.created_at,
            })
            
    # Sort combined orders descending by order ID
    orders.sort(key=lambda x: x.get('id') or 0, reverse=True)

    return render(request, 'staff/dashboard.html', {'orders': orders})

@login_required(login_url='staff_login')
def staff_update_order(request, order_id):
    if not request.user.is_staff:
        return redirect('staff_login')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            # 1) Update local snapshot
            order_local = Order.objects.get(id=order_id)
            order_local.status = new_status
            order_local.save()
            
            # 2) Sync to Order Microservice (Critical for Tracking UI)
            try:
                ms_payload = {'status': new_status.upper()} 
                requests.put(f'{GATEWAY_BASE}/orders/{order_id}', json=ms_payload, timeout=5)
            except Exception:
                pass
                
            # 3) Sync to Shipping Microservice (Ensures db reflects staff actions)
            try:
                shipping_payload = {'status': new_status.upper()}
                requests.put(f'http://shipping:8000/order/{order_id}/', json=shipping_payload, timeout=5)
            except Exception:
                pass

            messages.success(request, f'Order {order_local.tracking_id} updated to {new_status}')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            
    return redirect('staff_dashboard')

@login_required(login_url='staff_login')
def staff_import_product(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('staff_login')
    return render(request, 'staff/import_product.html')


# ---- ADMIN VIEWS ----

def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        if request.user.is_staff:
            return redirect('staff_dashboard')
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. You are not a superuser.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_portal/login.html', {'form': form})

def admin_register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True  # Admin registration creates a superuser
            user.save()
            messages.success(request, 'Admin account created successfully. Please login.')
            return redirect('admin_login')
    else:
        form = UserCreationForm()
    return render(request, 'admin_portal/register.html', {'form': form})

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('admin_login')
    
    # Fetch orders count from microservice
    orders_count = 0
    try:
        ord_resp = requests.get('http://order:8000/', timeout=2)
        if ord_resp.status_code == 200:
            orders_count = len(ord_resp.json())
    except:
        pass

    # Simple stats
    stats = {
        'users_count': User.objects.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'orders_count': orders_count,
    }
    return render(request, 'admin_portal/dashboard.html', {'stats': stats})

@login_required(login_url='admin_login')
def admin_add_user(request):
    if not request.user.is_superuser: return redirect('admin_login')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('admin_manage_users')
    else:
        form = UserCreationForm()
    return render(request, 'admin_portal/add_user.html', {'form': form})

@login_required(login_url='admin_login')
def admin_manage_users(request):
    if not request.user.is_superuser: return redirect('admin_login')
    users = User.objects.all().order_by('-id')
    return render(request, 'admin_portal/manage_users.html', {'users': users})

@login_required(login_url='admin_login')
def admin_toggle_user_role(request, user_id, role_type):
    if not request.user.is_superuser: return redirect('admin_login')
    target_user = get_object_or_404(User, id=user_id)
    
    if role_type == 'staff':
        target_user.is_staff = not target_user.is_staff
    elif role_type == 'admin':
        target_user.is_superuser = not target_user.is_superuser
        target_user.is_staff = True # Admin must be staff
        
    target_user.save()
    messages.success(request, f'Updated roles for {target_user.username}')
    return redirect('admin_manage_users')

@login_required(login_url='admin_login')
def admin_delete_user(request, user_id):
    if not request.user.is_superuser: return redirect('admin_login')
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot delete yourself.")
    else:
        target_user.delete()
        messages.success(request, f'Deleted user {target_user.username}')
    return redirect('admin_manage_users')

@login_required(login_url='admin_login')
def admin_manage_products(request):
    if not request.user.is_superuser: return redirect('admin_login')
    
    # Fetch products from product microservice
    try:
        response = requests.get('http://product:8000/', timeout=5)
        products = response.json() if response.status_code == 200 else []
        products.sort(key=lambda x: x.get('id', 0), reverse=True)
    except:
        products = []
        messages.error(request, "Could not connect to Product Microservice.")
        
    return render(request, 'admin_portal/manage_products.html', {'products': products})

@login_required(login_url='admin_login')
def admin_add_product(request):
    if not request.user.is_superuser: return redirect('admin_login')
    
    if request.method == 'POST':
        product_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price', 0)),
            'stock': int(request.POST.get('stock', 0)),
            'category': request.POST.get('category'),
            'image_url': request.POST.get('image_url')
        }
        
        try:
            response = requests.post('http://product:8000/add-product/', json=product_data, timeout=5)
            if response.status_code == 201:
                messages.success(request, f"Product '{product_data['name']}' added successfully.")
                return redirect('admin_manage_products')
            else:
                messages.error(request, f"Failed to add product: {response.text}")
        except:
            messages.error(request, "Connection error with Product Microservice.")
            
    return render(request, 'admin_portal/add_product.html')

@login_required(login_url='admin_login')
def admin_edit_product(request, product_id):
    if not request.user.is_superuser: return redirect('admin_login')
    
    if request.method == 'POST':
        product_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price', 0)),
            'stock': int(request.POST.get('stock', 0)),
            'category': request.POST.get('category'),
            'image_url': request.POST.get('image_url')
        }
        
        try:
            response = requests.post(f'http://product:8000/update-product/{product_id}/', json=product_data, timeout=5)
            if response.status_code == 200:
                messages.success(request, f"Product updated successfully.")
                return redirect('admin_manage_products')
            else:
                messages.error(request, f"Failed to update: {response.text}")
        except:
            messages.error(request, "Connection error.")
            
    # GET: Fetch current product data
    try:
        response = requests.get(f'http://product:8000/{product_id}/', timeout=5)
        product = response.json() if response.status_code == 200 else None
    except:
        product = None
        messages.error(request, "Could not fetch product details.")
        
    if not product: return redirect('admin_manage_products')
    return render(request, 'admin_portal/edit_product.html', {'product': product})

@login_required(login_url='admin_login')
def admin_delete_product(request, product_id):
    if not request.user.is_superuser: return redirect('admin_login')
    
    try:
        response = requests.delete(f'http://product:8000/delete-product/{product_id}/', timeout=5)
        if response.status_code in [200, 204]:
            messages.success(request, "Product deleted successfully.")
        else:
            messages.error(request, f"Failed to delete: {response.text}")
    except:
        messages.error(request, "Connection error.")
        
    return redirect('admin_manage_products')

@login_required(login_url='admin_login')
def admin_manage_orders(request):
    if not request.user.is_superuser: return redirect('admin_login')
    
    # Fetch all orders from order microservice
    try:
        response = requests.get('http://order:8000/', timeout=5)
        orders = response.json() if response.status_code == 200 else []
    except:
        orders = []
        messages.error(request, "Could not connect to Order Microservice.")
        
    return render(request, 'admin_portal/manage_orders.html', {'orders': orders})

@login_required(login_url='admin_login')
def admin_update_order_status(request, order_id):
    if not request.user.is_superuser: return redirect('admin_login')
    new_status = request.GET.get('status')
    if new_status:
        try:
            ms_payload = {'status': new_status.upper()}
            requests.put(f'http://order:8000/{order_id}', json=ms_payload, timeout=5)
            messages.success(request, f"Order #{order_id} marked as {new_status}")
        except Exception as e:
            messages.error(request, f"Failed to connect to Order service: {e}")
            
    return redirect('admin_manage_orders')
