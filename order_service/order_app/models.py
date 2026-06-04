from django.db import models

class Order(models.Model):
    tracking_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    user_id = models.IntegerField()
    full_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    total = models.FloatField(default=0.0)
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.CharField(max_length=100, null=True, blank=True)
    completed_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'orders'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'order_items'
