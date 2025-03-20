# alertas/tasks.py
from datetime import datetime, timedelta
from ordenes.models import OrdenesCompras
from ordenes.models import Solicitud
  # Asumiendo que tienes esta app y modelo
from alertas.models import Alerta

def revisar_ordenes_inactivas():
    # Revisar órdenes de compra en estado "pendiente" o "items pendientes" que no han cambiado a "completa" en 10 días
    limite = datetime.now() - timedelta(days=10)
    ordenes = OrdenesCompras.objects.filter(estado__in=['pendiente', 'items pendientes'], fecha__lte=limite)
    for oc in ordenes:
        mensaje = f"La OC {oc.numero_orden} no ha cambiado a 'completa' en 10 días."
        alerta_existente = Alerta.objects.filter(tipo='orden_no_actualizada', origen_id=oc.id, estado='pendiente').first()
        if not alerta_existente:
            Alerta.objects.create(
                tipo='orden_no_actualizada',
                mensaje=mensaje,
                origen_id=oc.id
            )

def revisar_solicitudes_inactivas():
    # Revisar solicitudes que no han cambiado de estado en 5 días
    limite = datetime.now() - timedelta(days=5)
    solicitudes = Solicitud.objects.filter(estado='pendiente', fecha_creacion__lte=limite)
    for sol in solicitudes:
        mensaje = f"La solicitud {sol.numero_solicitud} no ha cambiado de estado en 5 días."
        alerta_existente = Alerta.objects.filter(tipo='solicitud_no_actualizada', origen_id=sol.id, estado='pendiente').first()
        if not alerta_existente:
            Alerta.objects.create(
                tipo='solicitud_no_actualizada',
                mensaje=mensaje,
                origen_id=sol.id
            )

def revisar_stock_bajo():
    # Este ejemplo asume que el modelo Producto tiene stock_actual y stock_minimo.
    from bodega.models import Producto
    productos = Producto.objects.filter(stock_actual__lt=models.F('stock_minimo'))
    for prod in productos:
        mensaje = f"El producto {prod.nombre} (código {prod.codigo}) tiene stock bajo."
        alerta_existente = Alerta.objects.filter(tipo='stock_bajo', origen_id=prod.id, estado='pendiente').first()
        if not alerta_existente:
            Alerta.objects.create(
                tipo='stock_bajo',
                mensaje=mensaje,
                origen_id=prod.id
            )
