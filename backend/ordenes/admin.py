from django.contrib import admin
from .models import OrdenesCompras, OrdenCompraDetalle, Proveedor, Solicitud, SolicitudDetalle

# Inline para los detalles de Ordenes de Compra
class OrdenCompraDetalleInline(admin.TabularInline):
    model = OrdenCompraDetalle
    extra = 0
    fields = ('codigo_producto', 'detalle', 'cantidad', 'precio_unitario', 'cantidad_recibida')

@admin.register(OrdenesCompras)
class OrdenesComprasAdmin(admin.ModelAdmin):
    list_display   = ('numero_orden', 'fecha', 'empresa', 'proveedor', 'estado')
    search_fields  = ('numero_orden', 'nro_cotizacion', 'empresa', 'proveedor__nombre_proveedor')
    list_filter    = ('empresa', 'estado', 'fecha')
    date_hierarchy = 'fecha'
    ordering       = ('-fecha',)
    list_per_page  = 25
    inlines        = [OrdenCompraDetalleInline]

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display  = ('nombre_proveedor', 'rut', 'ubicacion', 'email', 'telefono')
    search_fields = ('nombre_proveedor', 'rut', 'ubicacion', 'email')
    list_filter   = ('ubicacion',)
    list_per_page = 25

# Inline para los detalles de Solicitud
class SolicitudDetalleInline(admin.TabularInline):
    model = SolicitudDetalle
    extra = 0
    fields = ('producto', 'cantidad', 'motivo', 'stock_bodega')
    readonly_fields = ('stock_bodega',)

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display   = (
        'numero_solicitud', 'folio', 'nro_cotizacion',
        'nombre_solicitante', 'usuario_creador',
        'estado', 'fecha_creacion'
    )
    search_fields  = (
        'numero_solicitud', 'folio', 'nro_cotizacion',
        'nombre_solicitante', 'usuario_creador__username',
        'estado', 'comentario'
    )
    list_filter    = ('estado', 'fecha_creacion')
    date_hierarchy = 'fecha_creacion'
    ordering       = ('-fecha_creacion',)
    list_per_page  = 25
    inlines        = [SolicitudDetalleInline]
