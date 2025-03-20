from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('bodeguero', 'Bodeguero'),
        ('secretario_tecnico', 'Secretario Técnico'),
        ('supervisor', 'Supervisor'),
        ('tecnico', 'Técnico'),
    )
    rol = models.CharField(max_length=30, choices=ROLE_CHOICES, default='bodeguero')

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
