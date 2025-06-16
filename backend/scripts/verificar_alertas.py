import os
import django
from datetime import datetime
from decimal import Decimal

# Setup del entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SolDega.settings')
django.setup()

from bodega.models import Producto, Alerta

def generar_alertas_stock_bajo():
    productos = Producto.objects.all()
    nuevas_alertas = 0

    for producto in productos:
        if producto.stock_minimo is not None and producto.cantidad <= producto.stock_minimo:
            mensaje = (
                f"El producto '{producto.nombre}' está bajo el stock mínimo "
                f"({producto.cantidad} ≤ {producto.stock_minimo}). Por favor crear solicitud."
            )
            # Verifica si ya existe una alerta sin resolver
            if not Alerta.objects.filter(producto=producto, resuelta=False).exists():
                Alerta.objects.create(producto=producto, mensaje=mensaje)
                nuevas_alertas += 1

    print(f"[{datetime.now()}] Verificación completada. {nuevas_alertas} nuevas alertas generadas.")

if __name__ == "__main__":
    generar_alertas_stock_bajo()
