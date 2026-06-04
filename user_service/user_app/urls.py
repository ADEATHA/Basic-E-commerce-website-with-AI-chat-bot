from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # ---- CUSTOMER ROUTES ----
    path('customer/login/', views.login_view, name='login'),
    path('customer/register/', views.register_view, name='register'),
    path('customer/logout/', views.logout_view, name='logout'),
    path('customer/shop/', views.shop, name='shop'),
    path('customer/cart/', views.cart_view, name='cart'),
    path('customer/checkout/', views.checkout, name='checkout'),
    path('customer/tracking/', views.tracking, name='tracking'),

    # ---- STAFF ROUTES ----
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/register/', views.staff_register_view, name='staff_register'),
    path('staff/logout/', views.staff_logout_view, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/order/update/<int:order_id>/', views.staff_update_order, name='staff_update_order'),
    path('staff/import/product/', views.staff_import_product, name='staff_import_product'),
    
    # Admin Portal (Custom)
    path('system-admin/login/', views.admin_login_view, name='admin_login'),
    path('system-admin/register/', views.admin_register_view, name='admin_register'),
    path('system-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('system-admin/users/', views.admin_manage_users, name='admin_manage_users'),
    path('system-admin/users/add/', views.admin_add_user, name='admin_add_user'),
    path('system-admin/users/toggle/<int:user_id>/<str:role_type>/', views.admin_toggle_user_role, name='admin_toggle_user_role'),
    path('system-admin/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('system-admin/products/', views.admin_manage_products, name='admin_manage_products'),
    path('system-admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('system-admin/products/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('system-admin/products/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('system-admin/orders/', views.admin_manage_orders, name='admin_manage_orders'),
    path('system-admin/orders/status/<int:order_id>/', views.admin_update_order_status, name='admin_update_order_status'),

    # ---- JWT AUTH ENDPOINTS (Shared) ----
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
