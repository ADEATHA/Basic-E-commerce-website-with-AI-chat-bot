from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField(unique=True)
    amount = models.FloatField(default=0.0)
    method = models.CharField(max_length=100, default='COD')
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'payments'
