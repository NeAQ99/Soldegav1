# movimientos/apps.py
from django.apps import AppConfig

class MovimientosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movimientos'

    def ready(self):
        import movimientos.signals