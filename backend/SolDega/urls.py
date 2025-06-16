from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from bodega.views import ProductoViewSet, AlertaViewSet  # ⬅️ Importa tu nuevo ViewSet
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'alertas', AlertaViewSet, basename='alerta')  # ⬅️ Registra el nuevo ViewSet
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('usuarios.urls')),
    path('api/movimientos/', include('movimientos.urls')),
    path('api/maquinaria/', include('maquinaria.urls')),
    path('api/ordenes/', include('ordenes.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    path('api/bodega/', include('bodega.urls')),
]
