from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'tipo',
            'precio_compra',
            'stock_actual',
            'stock_minimo',
            'consignacion',
            'nombre_consignacion',
            'ubicacion',
            'valor_total'
        ]
