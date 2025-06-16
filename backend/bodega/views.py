from rest_framework import viewsets
from .models import Producto
from django.db.models import F
from datetime import datetime
from .serializers import ProductoSerializer
from .models import Alerta
from .serializers import AlertaSerializer
from rest_framework.decorators import api_view  
from rest_framework.response import Response
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class AlertaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alerta.objects.filter(resuelta=False).order_by('-fecha')
    serializer_class = AlertaSerializer
    permission_classes = []  # Puedes ajustar permisos más adelante

@api_view(['POST'])
def generar_alertas_programadas(request):
    productos = Producto.objects.filter(stock_actual__lte=F('stock_minimo'))

    nuevas_alertas = []
    for producto in productos:
        existe = Alerta.objects.filter(producto=producto, resuelta=False).exists()
        if not existe:
            alerta = Alerta.objects.create(
                producto=producto,
                mensaje=f"Stock bajo el mínimo: {producto.nombre} ({producto.stock_actual} ≤ {producto.stock_minimo})"
            )
            nuevas_alertas.append(alerta.id)

    return Response({
        "mensaje": f"{len(nuevas_alertas)} alertas creadas",
        "ids": nuevas_alertas,
        "timestamp": datetime.now()
    })