# alertas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertaViewSet

router = DefaultRouter()
router.register(r'', AlertaViewSet, basename='alertas')

urlpatterns = [
    path('', include(router.urls)),
]
