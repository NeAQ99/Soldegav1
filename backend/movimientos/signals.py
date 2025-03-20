# movimientos/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entrada
from ordenes.models import OrdenesCompras

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Entrada)
def actualizar_orden_compra(sender, instance, created, **kwargs):
    # Procesa solo cuando se crea la entrada (evitando actualizaciones posteriores)
    if created and instance.orden_compra:
        oc = instance.orden_compra
        for detail in oc.detalles.all():
            # Comprueba si el detalle coincide con el producto de la entrada
            if instance.producto.codigo.lower().strip() == detail.detalle.lower().strip() or \
               (hasattr(instance.producto, 'nombre') and instance.producto.nombre.lower().strip() == detail.detalle.lower().strip()):
                logger.info(
                    f"Antes de actualizar: Detalle {detail.detalle}: Ordenado {detail.cantidad}, Recibido {detail.cantidad_recibida}"
                )
                detail.cantidad_recibida += instance.cantidad
                detail.save()
                logger.info(
                    f"Después de actualizar: Detalle {detail.detalle}: Ordenado {detail.cantidad}, Nuevo Recibido {detail.cantidad_recibida}, "
                    f"Pendiente {detail.cantidad - detail.cantidad_recibida}"
                )
        oc.actualizar_estado()
        logger.info(f"Estado actualizado de OC {oc.numero_orden}: {oc.estado}")
