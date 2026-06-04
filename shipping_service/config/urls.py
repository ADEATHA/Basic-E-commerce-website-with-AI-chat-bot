from django.urls import path
from shipping_app import views

urlpatterns = [
    path('', views.shipment_list_or_create),
    path('health', views.health),
    path('health/', views.health),
    path('order/<int:order_id>', views.get_shipment_by_order),
    path('order/<int:order_id>/', views.get_shipment_by_order),
]
