import threading
import os
from django.apps import AppConfig

class ShippingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shipping_app'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .consumers import start_consumer
            t = threading.Thread(target=start_consumer, daemon=True)
            t.start()
