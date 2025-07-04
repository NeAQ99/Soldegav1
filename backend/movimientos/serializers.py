from rest_framework import serializers
from .models import Entrada, Salida
from bodega.models import Producto
from ordenes.models import OrdenesCompras


class EntradaItemSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField()
    costo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    actualizar_precio = serializers.BooleanField(required=False, default=False)
    orden_compra = serializers.PrimaryKeyRelatedField(
        queryset=OrdenesCompras.objects.all(),
        required=False,
        allow_null=True
    )


class EntradaCreateSerializer(serializers.Serializer):
    motivo = serializers.CharField()
    comentario = serializers.CharField(allow_blank=True)
    items = EntradaItemSerializer(many=True)

    def create(self, validated_data):
        usuario = self.context['request'].user
        motivo = validated_data['motivo']
        comentario = validated_data['comentario']
        items = validated_data['items']
        entradas = []

        for item in items:
            producto = item['producto']
            cantidad = item['cantidad']
            costo_unitario = item['costo_unitario']
            orden_compra = item.get('orden_compra', None)

            entrada = Entrada.objects.create(
                usuario=usuario,
                motivo=motivo,
                comentario=comentario,
                producto=producto,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                orden_compra=orden_compra
            )

            producto.stock_actual += cantidad
            if item.get('actualizar_precio', False):
                producto.precio_compra = costo_unitario
            producto.save()

            entradas.append(entrada)

        return entradas
    
    class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'
    
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
