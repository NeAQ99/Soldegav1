from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
    filterset_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['codigo']
    pagination_class = None  # Desactiva paginación

    def get_queryset(self):
        queryset = Producto.objects.all().order_by('codigo')
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(nombre__icontains=search)[:25]
        return queryset[:20]