from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()  # ✅ Necesario para evitar errores con el router
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
    filterset_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['codigo']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get('search')

        if search:
            qs = qs.filter(nombre__icontains=search)
            return qs[:25]  # 🔚 Slice final
        return qs[:10]  # 🔚 Slice sin filtros ni ordenamientos adicionales
