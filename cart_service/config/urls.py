from django.urls import path
from cart_app import views

urlpatterns = [
    path('health', views.health),
    path('health/', views.health),
    path('<int:user_id>', views.get_cart),
    path('<int:user_id>/', views.get_cart),
    path('add', views.add_item),
    path('add/', views.add_item),
    path('remove', views.remove_item),
    path('remove/', views.remove_item),
]
