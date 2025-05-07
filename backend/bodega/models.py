from django.db import models

class Producto(models.Model):
    codigo = models.CharField(max_length=40, unique=True, db_index=True)
    nombre = models.CharField(max_length=100, db_index=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=50, db_index=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    consignacion = models.BooleanField(default=False)
    nombre_consignacion = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.CharField(max_length=100, db_index=True)


    @property
    def valor_total(self):
        return self.stock_actual * self.precio_compra

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
