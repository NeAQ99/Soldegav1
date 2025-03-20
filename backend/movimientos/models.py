from django.db import models
from django.conf import settings
from bodega.models import Producto
# Suponiendo que en una app "maquinaria" se define el modelo Maquinaria;
# de lo contrario, se puede definir aquí un modelo simple o dejarlo opcional.
# from maquinaria.models import Maquinaria  

class Entrada(models.Model):
    MOTIVO_CHOICES = (
        ('compra', 'Compra'),
        ('devolucion', 'Devolución'),
        ('recepcion_oc', 'Recepción de OC'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='entradas')
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entradas')
    fecha = models.DateTimeField(auto_now_add=True)
    orden_compra = models.ForeignKey('ordenes.OrdenesCompras', on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entrada: {self.producto.nombre} ({self.cantidad}) - {self.fecha}"

class Salida(models.Model):
    CARGO_CHOICES = (
        ('maquinaria', 'Maquinaria'),
        ('taller', 'Taller'),
        ('bodega', 'Bodega'),
        ('gerencia', 'Gerencia'),
        ('insumos', 'Insumos de Bodega'),
        ('otros', 'Otros'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='salidas')
    cantidad = models.PositiveIntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salidas')
    # Si el modelo Maquinaria existe, descomenta la siguiente línea:
    # maquinaria = models.ForeignKey(Maquinaria, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Salida: {self.producto.nombre} ({self.cantidad}) - {self.fecha}"
