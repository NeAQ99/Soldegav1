# movimientos/serializers.py
from rest_framework import serializers
from .models import Entrada, Salida
from bodega.models import Producto
from ordenes.models import OrdenesCompras


class EntradaItemSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField()
    costo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    orden_compra = serializers.PrimaryKeyRelatedField(
        queryset=OrdenesCompras.objects.all(), allow_null=True, required=False
    )
    actualizar_precio = serializers.BooleanField(default=False)


class EntradaSerializer(serializers.Serializer):
    motivo = serializers.CharField()
    comentario = serializers.CharField(allow_blank=True)
    items = EntradaItemSerializer(many=True)

def create(self, validated_data):
    usuario = self.context['request'].user
    motivo = validated_data['motivo']
    comentario = validated_data['comentario']
    items_data = validated_data['items']

    entradas = []
    for item_data in items_data:
        producto = item_data['producto']
        cantidad = item_data['cantidad']
        costo_unitario = item_data['costo_unitario']
        orden_compra = item_data.get('orden_compra')

        # Crear la entrada
        entrada = Entrada.objects.create(
            usuario=usuario,
            motivo=motivo,
            comentario=comentario,
            producto=producto,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            orden_compra=orden_compra
        )

        # Actualizar stock
        producto.stock_actual += cantidad

        # Si se indica que debe actualizar el precio
        if item_data.get('actualizar_precio', False):
            producto.precio_compra = costo_unitario

        producto.save()
        entradas.append(entrada)

    return entradas


class SalidaSerializer(serializers.ModelSerializer):
    producto_info = serializers.SerializerMethodField()

    class Meta:
        model = Salida
        fields = [
            'producto',
            'producto_info',
            'cantidad',
            'cargo',
            'comentario',
            'usuario',
            'fecha'
        ]
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    def get_producto_info(self, obj):
        return f"{obj.producto.codigo} - {obj.producto.nombre}"
