from django.db import models
from django.conf import settings
from django.db.models import Sum
from bodega.models import Producto

class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=100, unique=True)
    rut = models.CharField(max_length=20, unique=True)
    domicilio = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_proveedor

class Solicitud(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )
    numero_solicitud = models.CharField(max_length=20, unique=True)
    folio = models.CharField(max_length=20, blank=True, null=True)  # Campo ya existente
    nro_cotizacion = models.CharField(max_length=20, blank=True, null=True)  # NUEVO: Número de cotización
    nombre_solicitante = models.CharField(max_length=100)
    stock_bodega = models.CharField(max_length=50, blank=True, null=True)
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud {self.numero_solicitud} - {self.estado}"

class SolicitudDetalle(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='detalles')
    producto = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200)
    stock_bodega = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Detalle: {self.producto} - {self.cantidad}"

class OrdenesCompras(models.Model):
    numero_orden = models.CharField(max_length=20, unique=True)
    nro_cotizacion = models.CharField(max_length=20, blank=True, null=True)
    mercaderia_puesta_en = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    empresa = models.CharField(max_length=100)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50)
    forma_pago = models.CharField(max_length=50)
    plazo_entrega = models.CharField(max_length=50)
    comentarios = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')  # 'pendiente', 'items pendientes', 'completa'

    def __str__(self):
        return f"Orden {self.numero_orden} - {self.estado}"

    def actualizar_estado(self):
        all_zero = True
        all_complete = True
        for detail in self.detalles.all():
            if detail.cantidad_recibida > 0:
                all_zero = False
            if detail.cantidad_recibida < detail.cantidad:
                all_complete = False
        if all_complete:
            self.estado = 'completa'
        elif all_zero:
            self.estado = 'pendiente'
        else:
            self.estado = 'items pendientes'
        self.save()

class OrdenCompraDetalle(models.Model):
    orden = models.ForeignKey(OrdenesCompras, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.PositiveIntegerField()
    detalle = models.CharField(max_length=200)  # Almacenará el nombre (o código y nombre) del producto
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.PositiveIntegerField(default=0)
    # NUEVO: Campo para almacenar el código del producto
    codigo_producto = models.CharField(max_length=50, blank=True, null=True)

    @property
    def total_item(self):
        return self.cantidad * self.precio_unitario

    def cantidad_pendiente(self):
        return self.cantidad - self.cantidad_recibida

    def __str__(self):
        return f"Detalle de {self.orden.numero_orden}"
