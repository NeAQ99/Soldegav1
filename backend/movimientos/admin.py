from django.contrib import admin
from .models import Entrada, Salida

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'cantidad', 'costo_unitario',
        'usuario', 'fecha', 'orden_compra', 'motivo',
    )
    search_fields = (
        'producto__codigo',
        'producto__nombre',
        'usuario__username',
        'orden_compra__numero_orden',
        'motivo',
        'comentario',
    )
    list_filter = (
        'motivo',
        'fecha',
        'usuario',
        'orden_compra',
    )
    list_per_page = 25

@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'cantidad',
        'usuario', 'cargo', 'fecha',
    )
    search_fields = (
        'producto__codigo',
        'producto__nombre',
        'usuario__username',
        'cargo',
        'comentario',
    )
    list_filter = (
        'cargo',
        'fecha',
        'usuario',
    )
    list_per_page = 25
