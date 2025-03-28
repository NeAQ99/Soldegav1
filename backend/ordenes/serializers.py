from rest_framework import serializers
from .models import Proveedor, Solicitud, OrdenesCompras, OrdenCompraDetalle, SolicitudDetalle
from django.db.models import Max

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class SolicitudDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDetalle
        # Incluimos stock_bodega
        fields = ['id', 'producto', 'cantidad', 'motivo', 'stock_bodega']
        # Si deseas que se acepte "cargo" como alias de "motivo", se debe manejar en el front-end o en to_internal_value.

class SolicitudSerializer(serializers.ModelSerializer):
    usuario_creador = serializers.StringRelatedField(read_only=True)
    detalles = SolicitudDetalleSerializer(many=True, required=False)

    class Meta:
        model = Solicitud
        # Incluimos folio
        fields = [
            'id', 
            'numero_solicitud', 
            'folio',
            'nombre_solicitante', 
            'usuario_creador',
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
            'comentario',
            'detalles'
        ]
        extra_kwargs = {
            'numero_solicitud': {'read_only': True},
        }

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        # Generar el número de solicitud a partir de un número predeterminado
        last_sol = Solicitud.objects.aggregate(max_num=Max('numero_solicitud'))['max_num']
        if last_sol:
            try:
                new_num = int(last_sol) + 1
            except ValueError:
                new_num = 3400
        else:
            new_num = 3400
        # Asignar el nuevo número de solicitud al campo correspondiente
        validated_data['numero_solicitud'] = str(new_num)
        solicitud = Solicitud.objects.create(**validated_data)
        for detalle in detalles_data:
            SolicitudDetalle.objects.create(solicitud=solicitud, **detalle)
        return solicitud

class OrdenCompraDetalleSerializer(serializers.ModelSerializer):
    total_item = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = OrdenCompraDetalle
        fields = ['id', 'cantidad', 'detalle', 'precio_unitario', 'total_item', 'cantidad_pendiente']

    def get_cantidad_pendiente(self, obj):
        return obj.cantidad_pendiente()

class OrdenesComprasSerializer(serializers.ModelSerializer):
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        source='proveedor',
        write_only=True
    )
    proveedor = serializers.StringRelatedField(read_only=True)
    detalles = OrdenCompraDetalleSerializer(many=True, required=False)

    class Meta:
        model = OrdenesCompras
        fields = [
            'id', 'numero_orden', 'nro_cotizacion', 'mercaderia_puesta_en', 'fecha', 'empresa',
            'proveedor', 'proveedor_id', 'cargo', 'forma_pago', 'plazo_entrega', 'comentarios',
            'estado', 'detalles'
        ]
        extra_kwargs = {
            'numero_orden': {'read_only': True},
        }

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        last_order = self.Meta.model.objects.aggregate(max_num=Max('numero_orden'))['max_num']
        if last_order:
            try:
                new_num = int(last_order) + 1
            except ValueError:
                new_num = 7680
        else:
            new_num = 7680
        validated_data['numero_orden'] = str(new_num)
        orden = super().create(validated_data)
        for detalle_data in detalles_data:
            OrdenCompraDetalle.objects.create(orden=orden, **detalle_data)
        return orden