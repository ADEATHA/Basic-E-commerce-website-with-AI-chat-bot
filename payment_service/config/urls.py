from django.urls import path
from payment_app import views

urlpatterns = [
    path('', views.payment_list_or_create),
    path('health', views.health),
    path('health/', views.health),
    path('order/<int:order_id>', views.get_payment_by_order),
    path('order/<int:order_id>/', views.get_payment_by_order),
]
