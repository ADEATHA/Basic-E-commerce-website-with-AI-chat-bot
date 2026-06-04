from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'user', 'full_name', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_id', 'full_name', 'phone')
    ordering = ('-created_at',)

# Các model khác như Product, Category đã nằm ở các microservice khác, 
# nhưng Admin có thể quản lý trực tiếp qua Django Admin của User Service nếu ta đăng ký thêm các Proxy model 
# hoặc đơn giản là dùng trang Admin mặc định cho User.
