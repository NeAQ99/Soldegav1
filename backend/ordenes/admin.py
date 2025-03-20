# ordenes/admin.py
from django.contrib import admin
from .models import OrdenesCompras, OrdenCompraDetalle, Proveedor,Solicitud

class OrdenCompraDetalleInline(admin.TabularInline):
    model = OrdenCompraDetalle
    extra = 0  # o el número de formularios adicionales que desees

class OrdenesComprasAdmin(admin.ModelAdmin):
    inlines = [OrdenCompraDetalleInline]
    list_display = ('numero_orden', 'fecha', 'empresa', 'proveedor')

admin.site.register(OrdenesCompras, OrdenesComprasAdmin)
admin.site.register(Proveedor)

admin.site.register(Solicitud)