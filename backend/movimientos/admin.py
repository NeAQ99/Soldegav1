
from django.contrib import admin
from .models import  Salida,Entrada# Reemplaza 'Usuario' por el nombre de tu modelo

admin.site.register(Salida)
admin.site.register(Entrada)