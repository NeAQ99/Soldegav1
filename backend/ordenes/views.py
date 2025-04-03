import io
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.staticfiles import finders
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from ordenes.models import OrdenesCompras, OrdenCompraDetalle, Solicitud, Proveedor
from .serializers import (
    ProveedorSerializer,
    SolicitudSerializer,
    OrdenesComprasSerializer,
    OrdenCompraDetalleSerializer,
)
from django.db.models import Max

# Helper function para formatear números con separador de miles (punto) y decimal (coma)
def format_currency(value):
    # Ejemplo: 1111111.00 -> "1.111.111,00"
    s = "{:,.2f}".format(value)  # Genera "1,111,111.00"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by('nombre_proveedor')
    serializer_class = ProveedorSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all().order_by('-fecha_creacion')
    serializer_class = SolicitudSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_creador=self.request.user)

    @action(detail=True, methods=['patch'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        if not hasattr(request.user, 'rol') or request.user.rol not in ['supervisor', 'tecnico']:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        solicitud.estado = 'aprobada'
        solicitud.save()
        return Response({"status": "Solicitud aprobada"})

    @action(detail=True, methods=['patch'])
    def rechazar(self, request, pk=None):
        solicitud = self.get_object()
        if not hasattr(request.user, 'rol') or request.user.rol not in ['supervisor', 'tecnico']:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        solicitud.estado = 'rechazada'
        solicitud.save()
        return Response({"status": "Solicitud rechazada"})

class SolicitudPDFView(viewsets.ViewSet):
    """
    Endpoint para generar el PDF de una Solicitud.
    Se ha añadido la visualización del campo "nro_cotizacion".
    """
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        solicitud_id = request.query_params.get('solicitud_id')
        if not solicitud_id:
            return Response({"error": "Se requiere solicitud_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            solicitud = Solicitud.objects.get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        detalles = solicitud.detalles.all()
        detalle_header = ["Item", "Cantidad", "Insumo/Material Solicitado", "Cargo", "Stock Bodega"]
        if detalles.exists():
            detalle_data = [detalle_header] + [
                [
                    str(idx + 1),
                    str(det.cantidad),
                    det.producto,
                    det.motivo,
                    str(det.stock_bodega)
                ] for idx, det in enumerate(detalles)
            ]
        else:
            detalle_data = [detalle_header, ["-", "-", "-", "-", "-"]]
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        logo_path = finders.find("images/logo.png")
        logo_element = None
        if logo_path:
            try:
                logo_element = Image(logo_path, width=100, height=50)
                logo_element.hAlign = 'LEFT'
            except Exception as e:
                print("Error cargando el logo:", e)
        header_data = [[
            logo_element if logo_element else "",
            Paragraph(f"<b style='font-size:18px;'>Folio: {solicitud.folio if solicitud.folio else 'n/a'}</b>", styles['Normal'])
        ]]
        header_table = Table(header_data, colWidths=[150, 350])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))
        
        # Información de la solicitud, incluyendo N° Cotización
        info_data = [
            ["Fecha:", solicitud.fecha_creacion.strftime("%d/%m/%Y")],
            ["Solicitante:", solicitud.nombre_solicitante],
            ["Usuario Creador:", solicitud.usuario_creador.username if solicitud.usuario_creador else "n/a"],
            ["N° Cotización:", solicitud.nro_cotizacion if solicitud.nro_cotizacion else "n/a"]
        ]
        info_table = Table(info_data, colWidths=[120, 380])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Solicitud de Compra de Materiales e Insumos", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Generación de la tabla de detalles con separación del código
        detalle_table = Table(detalle_data, repeatRows=1, colWidths=[50, 80, 200, 100, 80])
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkgray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        elements.append(detalle_table)
        elements.append(Spacer(1, 24))

        firmas_data = [
            ["Firma Solicitante", "Firma Bodeguero", "Firma Jefe de Area", "Firma Gerente Faena"],
            ["________________", "________________", "________________", "________________"],
        ]
        firmas_table = Table(firmas_data, colWidths=[120, 120, 120, 120], hAlign='CENTER')
        firmas_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,1), 10),
            ('TOPPADDING', (0,1), (-1,1), 12),
        ]))
        elements.append(firmas_table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="solicitud.pdf"'
        response.write(pdf)
        return response

class OrdenesComprasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las órdenes de compra.
    Se asigna el correlativo de forma independiente según la empresa.
    """
    queryset = OrdenesCompras.objects.all().order_by('-fecha')
    serializer_class = OrdenesComprasSerializer

    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        pendientes_oc = self.get_queryset().filter(estado__in=['pendiente', 'items pendientes'])
        serializer = self.get_serializer(pendientes_oc, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        orders_to_update = self.get_queryset().filter(
            fecha__lt=thirty_days_ago,
            estado__in=['pendiente', 'producto pendiente']
        )
        orders_to_update.update(estado='inactiva')
        return super().list(request, *args, **kwargs)

class OrdenCompraDetalleViewSet(viewsets.ModelViewSet):
    queryset = OrdenCompraDetalle.objects.all()
    serializer_class = OrdenCompraDetalleSerializer

class OrdenesPDFView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        # Se obtiene el parámetro 'orden_id' de la query string
        orden_id = request.query_params.get('orden_id')
        if not orden_id:
            return Response({"error": "Se requiere orden_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            orden = OrdenesCompras.objects.get(id=orden_id)
        except OrdenesCompras.DoesNotExist:
            return Response({"error": "Orden no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        # Se obtienen los detalles asociados a la orden
        detalles = orden.detalles.all()

        # Se define el header de la tabla de detalles, incluyendo la columna "Código"
        detalle_header = ["Cantidad", "Código", "Producto / Detalle", "Precio Unitario", "Total Producto"]
        detalle_data = [detalle_header]

        # Procesar cada detalle para extraer y separar el código si es necesario
        if detalles:
            for detalle in detalles:
                cantidad = detalle.cantidad
                # Si no hay 'codigo_producto' y en 'detalle' se encuentra ":", se separa en código y nombre
                if not detalle.codigo_producto and ":" in detalle.detalle:
                    parts = detalle.detalle.split(":", 1)
                    codigo = parts[0].strip()
                    producto = parts[1].strip()
                else:
                    codigo = detalle.codigo_producto if detalle.codigo_producto else "-"
                    producto = detalle.detalle
                precio_unitario = float(detalle.precio_unitario)
                total_producto = float(detalle.total_item)
                detalle_data.append([
                    str(cantidad),
                    codigo,
                    producto,
                    f"${format_currency(precio_unitario)}",
                    f"${format_currency(total_producto)}"
                ])
        else:
            detalle_data.append(["-", "-", "No hay detalles", "-", "-"])

        # Cálculo de totales usando Decimal para evitar problemas de precisión
        total_neto = sum([Decimal(detalle.cantidad) * detalle.precio_unitario for detalle in detalles])
        iva = total_neto * Decimal('0.19')
        total_orden = total_neto + iva

        # Inicializa el buffer para el PDF y crea el documento
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Cargar el logo
        logo_path = finders.find("images/logo.png")
        logo_element = None
        if logo_path:
            try:
                logo_element = Image(logo_path, width=100, height=50)
                logo_element.hAlign = 'LEFT'
            except Exception as e:
                print("Error cargando el logo:", e)
        else:
            print("Logo no encontrado en static/images/logo.png")

        # Header: se muestra el logo (sin el folio, que se mostrará en la tabla de información)
        header_data = [[
            logo_element if logo_element else ""
        ]]
        # Ajusta los anchos de columna (por ejemplo, [150, 350] si se desea espacio para otro contenido, pero aquí solo usamos el logo)
        header_table = Table(header_data, colWidths=[150])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Se ajusta el padding para controlar el espacio
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))

        # Construcción de la tabla de información de la orden
        # Se muestra N° Orden, Fecha, N° Cotización, Empresa, Merc. Puesta en, Proveedor, Rut, Domicilio, Folio y Ciudad
        orden_data = []
        orden_data.append([
            "N° Orden:", orden.numero_orden,
            "Fecha:", orden.fecha.strftime("%d/%m/%Y")
        ])
        orden_data.append([
            "N° Cotización:", orden.nro_cotizacion if orden.nro_cotizacion else "n/a",
            "Empresa:", orden.empresa
        ])
        orden_data.append([
            "Merc. Puesta en:", orden.mercaderia_puesta_en if orden.mercaderia_puesta_en else "n/a",
            "Proveedor:", orden.proveedor.nombre_proveedor if orden.proveedor else "n/a"
        ])
        orden_data.append([
            "Rut:", orden.proveedor.rut if orden.proveedor else "n/a",
            "Domicilio:", orden.proveedor.domicilio if orden.proveedor else "n/a"
        ])
        # Nueva fila que muestra "Folio" y "Cargo" en dos columnas
        orden_data.append([
            "Folio:", orden.folio if hasattr(orden, 'folio') and orden.folio else "n/a",
            "Cargo:", orden.cargo if orden.cargo else "n/a"
        ])
        # Última fila para mostrar la Ciudad
        orden_data.append([
            "Ciudad:", orden.proveedor.ubicacion if orden.proveedor else "n/a",
            "", ""
        ])

        header_table_order = Table(orden_data, colWidths=[100, 150, 100, 150])
        header_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Se aplican fondos a las etiquetas para mayor claridad
            ('BACKGROUND', (0, 0), (0, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (0, 1), colors.whitesmoke),
            ('BACKGROUND', (0, 2), (0, 2), colors.whitesmoke),
            ('BACKGROUND', (0, 3), (0, 3), colors.whitesmoke),
            ('BACKGROUND', (0, 4), (0, 4), colors.whitesmoke),
            ('BACKGROUND', (2, 0), (2, 0), colors.whitesmoke),
            ('BACKGROUND', (2, 1), (2, 1), colors.whitesmoke),
            ('BACKGROUND', (2, 2), (2, 2), colors.whitesmoke),
            ('BACKGROUND', (2, 3), (2, 3), colors.whitesmoke),
        ])
        header_table_order.setStyle(header_style)
        elements.append(header_table_order)
        elements.append(Spacer(1, 12))

        # Tabla de detalles de la orden
        detalle_table = Table(detalle_data, repeatRows=1)
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(detalle_table)
        elements.append(Spacer(1, 12))

        # Tabla de totales
        totales_data = [
            ["Total Neto:", f"${format_currency(total_neto)}"],
            ["IVA (19%):", f"${format_currency(iva)}"],
            ["Total Orden:", f"${format_currency(total_orden)}"],
        ]
        totales_table = Table(totales_data, colWidths=[150, 100], hAlign='RIGHT')
        totales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(1, 12))

        # Tabla de información adicional (Plazo, Forma de pago, Comentarios)
        additional_data = [
            ["Plazo de entrega:", orden.plazo_entrega],
            ["Forma de pago:", orden.forma_pago],
            ["Comentarios:", orden.comentarios or ""],
        ]
        additional_table = Table(additional_data, colWidths=[150, 300], hAlign='LEFT')
        additional_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(additional_table)
        elements.append(Spacer(1, 24))

        # Tabla de firmas
        firmas_data = [
            ["Jefe Faena", "Solicitante", "Contabilidad"],
            ["________________________", "________________________", "________________________"],
        ]
        firmas_table = Table(firmas_data, colWidths=[150, 150, 150], hAlign='CENTER')
        firmas_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 12),
        ]))
        elements.append(firmas_table)

        # Se construye el PDF, se obtiene el contenido y se retorna como respuesta HTTP
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orden_compra.pdf"'
        response.write(pdf)
        return response
