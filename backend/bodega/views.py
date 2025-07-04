from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['nombre', 'categoria']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['codigo']
    serializer_class = ProductoSerializer
