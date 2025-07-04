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
        motivo = validated_data.get('motivo')
        comentario = validated_data.get('comentario')
        items_data = validated_data.pop('items', [])

        entradas = []
        for item in items_data:
            entrada = Entrada.objects.create(
                usuario=usuario,
                motivo=motivo,
                comentario=comentario,
                producto=item['producto'],
                cantidad=item['cantidad'],
                costo_unitario=item['costo_unitario'],
                orden_compra=item.get('orden_compra')
            )
            producto = item['producto']
            producto.stock_actual += int(item['cantidad'])
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
