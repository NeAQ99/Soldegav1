from rest_framework import serializers
from .models import Maquinaria

class MaquinariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquinaria
        fields = ['id', 'nro_equipo', 'tipo', 'patente']
