from django.db import models
from django.contrib.auth.models import User
import uuid

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, unique=True, null=True)
    
    # Shipping info
    full_name = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=20, null=True)
    
    # Order details (Simplified for this microservice demo)
    # in a real app, this would be a JSONField or a separate OrderItem model
    items_json = models.TextField(null=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(default='Pending', max_length=50) # for tracking
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = "ORD-" + str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.tracking_id} - {self.status}"
