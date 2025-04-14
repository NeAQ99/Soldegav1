from django.db import models
from django.conf import settings
from bodega.models import Producto

class Entrada(models.Model):
    MOTIVO_CHOICES = (
        ('compra', 'Compra'),
        ('devolucion', 'Devolución'),
        ('recepcion_oc', 'Recepción de OC'),
    )
    # Relación con Producto (ForeignKey ya tiene índice por defecto)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='entradas')
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # Relación con Usuario (ForeignKey con índice por defecto)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entradas')
    # Campo fecha indexado para búsquedas y ordenación
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    # Relación con OrdenesCompras, indexada para acelerar filtros por orden de compra
    orden_compra = models.ForeignKey('ordenes.OrdenesCompras', on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    # Campo motivo indexado para filtrados rápidos
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES, db_index=True)
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
    # Relación con Producto (ForeignKey ya indexa automáticamente)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='salidas')
    cantidad = models.PositiveIntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salidas')
    # Si el modelo Maquinaria existe, podrías descomentar la siguiente línea para indexarlo también
    # maquinaria = models.ForeignKey(Maquinaria, on_delete=models.SET_NULL, null=True, blank=True)
    # Campo cargo indexado para filtrados rápidos (p.ej., para ver salidas por taller, maquinaria, etc.)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, db_index=True)
    comentario = models.TextField(blank=True, null=True)
    # Campo fecha indexado para búsquedas y ordenaciones
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Salida: {self.producto.nombre} ({self.cantidad}) - {self.fecha}"
