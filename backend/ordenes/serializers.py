
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
        fields = ['id', 'producto', 'cantidad', 'motivo', 'stock_bodega']

class SolicitudSerializer(serializers.ModelSerializer):
    usuario_creador = serializers.StringRelatedField(read_only=True)
    detalles = SolicitudDetalleSerializer(many=True, required=False)
    nro_cotizacion = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # NUEVO: Campo nro_cotizacion

    class Meta:
        model = Solicitud
        fields = [
            'id', 
            'numero_solicitud', 
            'folio',
            'nro_cotizacion',  # Se incluye en la lista de campos
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
        # Genera el número de solicitud automáticamente
        last_sol = Solicitud.objects.aggregate(max_num=Max('numero_solicitud'))['max_num']
        if last_sol:
            try:
                new_num = int(last_sol) + 1
            except ValueError:
                new_num = 3400
        else:
            new_num = 3400
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
        fields = ['id', 'cantidad', 'detalle', 'precio_unitario', 'total_item', 'cantidad_pendiente', 'codigo_producto']

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
            empresa = validated_data.get('empresa')
            if empresa == "Inversiones Imperia SPA":
                last_order = self.Meta.model.objects.filter(empresa="Inversiones Imperia SPA").aggregate(max_num=Max('numero_orden'))['max_num']
                start = 7698  # Número predeterminado para Inversiones Imperia SPA
            elif empresa == "Maquinarias Imperia SPA":
                last_order = self.Meta.model.objects.filter(empresa="Maquinarias Imperia SPA").aggregate(max_num=Max('numero_orden'))['max_num']
                start = 280  # Número predeterminado para Maquinarias Imperia SPA (ajústalo según necesites)
            else:
                raise serializers.ValidationError("Empresa inválida. Las opciones permitidas son 'Inversiones Imperia SPA' y 'Maquinarias Imperia SPA'.")

            if last_order:
                try:
                    new_num = int(last_order) + 1
                except ValueError:
                    new_num = start
            else:
                new_num = start

            validated_data['numero_orden'] = str(new_num)
            orden = OrdenesCompras.objects.create(**validated_data)
            for detalle_data in detalles_data:
                if isinstance(detalle_data.get('detalle'), dict):
                    detalle_data['codigo_producto'] = detalle_data['detalle'].get('codigo', '')
                    detalle_data['detalle'] = detalle_data['detalle'].get('nombre', '')
                OrdenCompraDetalle.objects.create(orden=orden, **detalle_data)
            return orden

