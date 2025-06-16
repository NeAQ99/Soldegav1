# bodega/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductoViewSet, AlertaViewSet, generar_alertas_programadas

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'alertas', AlertaViewSet, basename='alerta')

urlpatterns = [
    path('', include(router.urls)),
    path('generar_alertas_programadas/', generar_alertas_programadas, name='generar_alertas_programadas'),
]
