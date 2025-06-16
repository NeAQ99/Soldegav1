from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, AlertaViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'alertas', AlertaViewSet, basename='alerta')

urlpatterns = [
    path('', include(router.urls)),
]
