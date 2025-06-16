from django.urls import path
from .views import generar_alertas_programadas

urlpatterns = [
    path('generar_alertas_programadas/', generar_alertas_programadas, name='generar_alertas_programadas'),
]
