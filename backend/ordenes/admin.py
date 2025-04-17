from django.contrib import admin
from .models import OrdenesCompras, OrdenCompraDetalle, Proveedor, Solicitud

class OrdenCompraDetalleInline(admin.TabularInline):
    model = OrdenCompraDetalle
    extra = 0

@admin.register(OrdenesCompras)
class OrdenesComprasAdmin(admin.ModelAdmin):
    inlines = [OrdenCompraDetalleInline]
    list_display = (
        'numero_orden',
        'fecha',
        'empresa',
        'proveedor',
        'estado',
    )
    search_fields = (
        'numero_orden',
        'nro_cotizacion',
        'empresa',
        'proveedor__nombre_proveedor',
        'estado',
    )
    list_filter = (
        'empresa',
        'estado',
        'fecha',
    )
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    list_per_page = 25

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_proveedor', 'rut', 'ubicacion', 'email')
    search_fields = ('nombre_proveedor', 'rut', 'ubicacion', 'email')
    list_filter = ('ubicacion',)
    list_per_page = 25

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'numero_solicitud',
        'folio',
        'nro_cotizacion',
        'nombre_solicitante',
        'usuario_creador',
        'estado',
        'fecha_creacion',
    )
    search_fields = (
        'numero_solicitud',
        'folio',
        'nro_cotizacion',
        'nombre_solicitante',
        'usuario_creador__username',
        'estado',
        'comentario',
    )
    list_filter = (
        'estado',
        'fecha_creacion',
    )
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    list_per_page = 25
