# movimientos/serializers.py
from rest_framework import serializers
from .models import Entrada, Salida
from ordenes.serializers import OrdenesComprasSerializer  # O crea un campo personalizado

class EntradaSerializer(serializers.ModelSerializer):
    producto_info = serializers.SerializerMethodField()
    # Nuevo: campo para incluir la información de la OC
    orden_compra_info = serializers.SerializerMethodField()

    class Meta:
        model = Entrada
        fields = ['producto', 'producto_info', 'cantidad', 'costo_unitario', 'motivo', 'comentario', 'usuario', 'fecha', 'orden_compra', 'orden_compra_info']
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    def get_producto_info(self, obj):
        return f"{obj.producto.codigo} - {obj.producto.nombre}"

    def get_orden_compra_info(self, obj):
        if obj.orden_compra:
            return f"OC {obj.orden_compra.numero_orden}"
        return None

class SalidaSerializer(serializers.ModelSerializer):
    producto_info = serializers.SerializerMethodField()

    class Meta:
        model = Salida
        fields = ['producto', 'producto_info', 'cantidad', 'cargo', 'comentario', 'usuario', 'fecha']
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    def get_producto_info(self, obj):
        return f"{obj.producto.codigo} - {obj.producto.nombre}"
