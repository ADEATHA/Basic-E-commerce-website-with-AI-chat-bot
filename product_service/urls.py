from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('<int:pk>/', views.product_detail, name='product-detail'),
    path('record-purchase/', views.record_purchase, name='record-purchase'),
    path('add-product/', views.add_product, name='add-product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete-product'),
    path('update-product/<int:pk>/', views.update_product, name='update-product'),
]
