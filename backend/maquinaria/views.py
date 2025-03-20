from rest_framework import viewsets
from .models import Maquinaria
from .serializers import MaquinariaSerializer

class MaquinariaViewSet(viewsets.ModelViewSet):
    queryset = Maquinaria.objects.all().order_by('nro_equipo')
    serializer_class = MaquinariaSerializer
