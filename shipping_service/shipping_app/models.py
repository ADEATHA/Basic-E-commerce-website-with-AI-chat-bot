from django.db import models

class Shipment(models.Model):
    order_id = models.IntegerField(unique=True)
    carrier = models.CharField(max_length=255, default='Standard Express')
    status = models.CharField(max_length=50, default='PREPARING')
    created_at = models.CharField(max_length=100, null=True, blank=True)
    delivered_at = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'shipments'
