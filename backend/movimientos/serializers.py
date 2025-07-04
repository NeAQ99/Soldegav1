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


class EntradaSerializer(serializers.ModelSerializer):
    items = EntradaItemSerializer(many=True)
    comentario = serializers.CharField(allow_blank=True)

    class Meta:
        model = Entrada
        fields = ['motivo', 'comentario', 'items']

    def create(self, validated_data):
        usuario = self.context['request'].user
        motivo = validated_data.get('motivo')
        comentario = validated_data.get('comentario')
        items_data = validated_data.pop('items', [])

        entradas_creadas = []

        for item in items_data:
            producto = item['producto']
            cantidad = item['cantidad']
            costo_unitario = item['costo_unitario']
            orden_compra = item.get('orden_compra')

            entrada = Entrada.objects.create(
                usuario=usuario,
                motivo=motivo,
                comentario=comentario,
                producto=producto,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                orden_compra=orden_compra,
            )

            # Actualizar stock
            producto.stock_actual += cantidad
            producto.save()

            entradas_creadas.append(entrada)

        return entradas_creadas[0] if len(entradas_creadas) == 1 else entradas_creadas
    
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
