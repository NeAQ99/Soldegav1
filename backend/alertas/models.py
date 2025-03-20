# alertas/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

ALERTA_TIPO_CHOICES = (
    ('salida_alta', 'Salida de alto valor'),
    ('orden_no_actualizada', 'Orden sin actualización'),
    ('solicitud_no_actualizada', 'Solicitud sin actualización'),
    ('stock_bajo', 'Producto con stock bajo'),
)

ALERTA_ESTADO_CHOICES = (
    ('pendiente', 'Pendiente'),
    ('resuelta', 'Resuelta'),
    ('rechazada', 'Rechazada'),
)

class Alerta(models.Model):
    tipo = models.CharField(max_length=50, choices=ALERTA_TIPO_CHOICES)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ALERTA_ESTADO_CHOICES, default='pendiente')
    # Enlace opcional al objeto origen, por ejemplo, una orden
    origen_id = models.PositiveIntegerField(null=True, blank=True)
    # Comentario al resolver la alerta
    comentario_resolucion = models.TextField(blank=True, null=True)
    # Quién resolvió la alerta (opcional)
    resuelta_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Alerta [{self.tipo}] - {self.estado} - {self.mensaje[:30]}"
