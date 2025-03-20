from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from bodega.views import ProductoViewSet

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('usuarios.urls')),
    path('api/movimientos/', include('movimientos.urls')),
    path('api/maquinaria/', include('maquinaria.urls')),
    path('api/ordenes/', include('ordenes.urls')),
    path('api/', include('ordenes.urls')),
    path('api/alertas/', include('alertas.urls')),


]
