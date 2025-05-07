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
    nro_cotizacion = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Solicitud
        fields = [
            'id', 
            'numero_solicitud', 
            'folio',
            'nro_cotizacion',
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
            'id',
            'numero_orden',
            'nro_cotizacion',
            'mercaderia_puesta_en',
            'fecha',
            'empresa',
            'proveedor',
            'proveedor_id',
            'cargo',
            'forma_pago',
            'plazo_entrega',
            'comentarios',
            'estado',
            'detalles',
        ]
    extra_kwargs = {
        'numero_orden': {'read_only': True},
    }

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        empresa = validated_data.get('empresa', '').strip().lower()

        # Defino el correlativo inicial por si no hay ninguna OC previa
        if empresa == "inversiones imperia spa":
            last_order = OrdenesCompras.objects.filter(
                empresa__iexact="Inversiones Imperia Spa"
            ).aggregate(max_num=Max('numero_orden'))['max_num']
            start = 7788

        elif empresa == "maquinarias imperia spa":
            last_order = OrdenesCompras.objects.filter(
                empresa__iexact="Maquinarias Imperia SPA"
            ).aggregate(max_num=Max('numero_orden'))['max_num']
            start = 265

        else:
            raise serializers.ValidationError(
                "Empresa inválida. Las opciones permitidas son "
                "'Inversiones Imperia Spa' y 'Maquinarias Imperia SPA'."
            )

        # Si existe un correlativo previo, tomo +1; si no, uso el start
        if last_order:
            try:
                next_num = int(last_order) + 1
            except (TypeError, ValueError):
                next_num = start
        else:
            next_num = start

        # Sólo para Inversiones: si el siguiente sería 7787, lo salto a 7788
        if empresa == "inversiones imperia spa" and next_num == 7787:
            next_num = 7788

        validated_data['numero_orden'] = str(next_num)

        # Creo la orden y sus detalles
        orden = OrdenesCompras.objects.create(**validated_data)
        for detalle in detalles_data:
            det = detalle.copy()
            if isinstance(det.get('detalle'), dict):
                det['codigo_producto'] = det['detalle'].get('codigo', '')
                det['detalle'] = det['detalle'].get('nombre', '')
            OrdenCompraDetalle.objects.create(orden=orden, **det)

        return orden
