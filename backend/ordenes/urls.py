from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudViewSet, SolicitudPDFView, OrdenesComprasViewSet, OrdenCompraDetalleViewSet, ProveedorViewSet, OrdenesPDFView

router = DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedores')
router.register(r'solicitudes', SolicitudViewSet, basename='solicitudes')
router.register(r'solicitudes/reporte', SolicitudPDFView, basename='solicitudes-reporte')
router.register(r'ordenes', OrdenesComprasViewSet, basename='ordenes')
router.register(r'ordenes/reporte', OrdenesPDFView, basename='ordenes-reporte')
router.register(r'detalles', OrdenCompraDetalleViewSet, basename='detalles')

urlpatterns = [
    path('', include(router.urls)),
]
