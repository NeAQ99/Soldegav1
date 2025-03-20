from rest_framework import serializers
from .models import Entrada, Salida

class EntradaSerializer(serializers.ModelSerializer):
    producto_info = serializers.SerializerMethodField()

    class Meta:
        model = Entrada
        fields = ['producto', 'producto_info', 'cantidad', 'costo_unitario', 'motivo', 'comentario', 'usuario', 'fecha', 'orden_compra']
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    def get_producto_info(self, obj):
        # Retorna "código - nombre" del producto relacionado
        return f"{obj.producto.codigo} - {obj.producto.nombre}"


class SalidaSerializer(serializers.ModelSerializer):
    producto_info = serializers.SerializerMethodField()

    class Meta:
        model = Salida
        fields = ['producto', 'producto_info', 'cantidad', 'cargo', 'comentario', 'usuario', 'fecha']
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    def get_producto_info(self, obj):
        # Retorna "código - nombre" del producto relacionado
        return f"{obj.producto.codigo} - {obj.producto.nombre}"