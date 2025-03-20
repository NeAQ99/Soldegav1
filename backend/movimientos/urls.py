from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EntradaViewSet, SalidaViewSet, ReportePDFView

router = DefaultRouter()
router.register(r'entradas', EntradaViewSet)
router.register(r'salidas', SalidaViewSet)
router.register(r'reporte', ReportePDFView, basename='reporte')

urlpatterns = [
    path('', include(router.urls)),
]
