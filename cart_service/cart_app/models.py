from django.db import models

class CartItem(models.Model):
    user_id = models.IntegerField()
    product_id = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    updated_at = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('user_id', 'product_id')
