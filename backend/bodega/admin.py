from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas que se muestran en la lista
    list_display = (
        'codigo',
        'nombre',
        'stock_actual',
        'stock_minimo',
        'precio_compra',
        'ubicacion',
        'consignacion',
    )
    # Campos en los que se puede buscar
    search_fields = (
        'codigo',
        'nombre',
        'descripcion',
        'ubicacion',
        'consignacion', 
    )
    # Filtros laterales
    list_filter = (
        'consignacion',
        'ubicacion',
    )
    # Paginación en el admin (opcional)
    list_per_page = 25
