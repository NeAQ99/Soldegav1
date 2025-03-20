from django.db import models

class Maquinaria(models.Model):
    TIPO_CHOICES = (
        ('camioneta', 'Camioneta'),
        ('camion', 'Camión'),
        ('extraccion', 'Extracción'),
        ('batea', 'Batea'),
        ('otros', 'Otros'),
    )
    nro_equipo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    patente = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nro_equipo} - {self.tipo} - {self.patente}"
