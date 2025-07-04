from rest_framework import viewsets
from django.db.models import Q
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    pagination_class = None  # Sin paginación

    def get_queryset(self):
        queryset = Producto.objects.all().order_by('codigo')
        search = self.request.query_params.get('search')

        if search:
            return queryset.filter(
                Q(nombre__icontains=search) |
                Q(codigo__icontains=search)
            )[:25]
        return queryset[:10]