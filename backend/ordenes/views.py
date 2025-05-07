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
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

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
        orden_id = request.query_params.get('orden_id')
        if not orden_id:
            return Response(
                {"error": "Se requiere orden_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            orden = OrdenesCompras.objects.get(id=orden_id)
        except OrdenesCompras.DoesNotExist:
            return Response(
                {"error": "Orden no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

        detalles = orden.detalles.all()

        # --- Estilos y Paragraph para contenido largo ---
        styles     = getSampleStyleSheet()
        body_style = ParagraphStyle(
            name='body',
            parent=styles['BodyText'],
            wordWrap='CJK',      # envuelve líneas automáticamente
            alignment=TA_LEFT,   # alineación izquierda
            leading=12,          # espacio entre líneas
        )

        # --- Header de tabla de detalles ---
        detalle_header = [
            "Cantidad",
            "Código",
            "Producto / Detalle",
            "Precio Unitario",
            "Total Producto"
        ]
        detalle_data = [detalle_header]

        # Llenar filas, convirtiendo el texto largo en Paragraph
        for det in detalles:
            cant = det.cantidad

            if not det.codigo_producto and ":" in det.detalle:
                parts  = det.detalle.split(":", 1)
                codigo = parts[0].strip()
                nombre = parts[1].strip()
            else:
                codigo = det.codigo_producto or "-"
                nombre = det.detalle

            nombre_para = Paragraph(nombre, body_style)

            pu = float(det.precio_unitario)
            tp = float(det.total_item)

            detalle_data.append([
                str(cant),
                codigo,
                nombre_para,
                f"${format_currency(pu)}",
                f"${format_currency(tp)}"
            ])

        if not detalles:
            detalle_data.append(["-", "-", "No hay detalles", "-", "-"])

        # --- Cálculo de totales ---
        total_neto  = sum(
            Decimal(d.cantidad) * d.precio_unitario
            for d in detalles
        )
        iva         = total_neto * Decimal('0.19')
        total_orden = total_neto + iva

        # --- Configuración del PDF ---
        buffer = io.BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Logo y dirección
        logo_path = finders.find("images/logo.png")
        if logo_path:
            logo_el = Image(logo_path, width=100, height=50)
            logo_el.hAlign = 'CENTER'
        else:
            logo_el = ""

        address_text = (
            "52.001.387-3<br/>"
            "Bolivar #202<br/>"
            "Edificio Finanzas<br/>"
            "Oficina #511"
        )
        address_para = Paragraph(address_text, styles["Normal"])

        header_table = Table(
            [[logo_el, address_para]],
            colWidths=[200, 300]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',         (0,0), (0,0),     'CENTER'),
            ('ALIGN',         (1,0), (1,0),     'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1),   12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))

        # --- Información de la orden ---
        orden_info = [
            ["Número de Orden:", str(orden.id)],
            ["Fecha:", orden.fecha.strftime("%d/%m/%Y")],
            ["Proveedor:", orden.proveedor_nombre],
            ["RUT Proveedor:", orden.proveedor_rut],
            ["Dirección Proveedor:", orden.proveedor_direccion],
            ["Destinatario:", orden.destinatario or "-"],
        ]
        order_table = Table(
            orden_info,
            colWidths=[120, 380],
            hAlign="LEFT"
        )
        order_table.setStyle(TableStyle([
            ('FONTNAME',       (0,0), (-1,-1),    'Helvetica'),
            ('FONTSIZE',       (0,0), (-1,-1),    10),
            ('VALIGN',         (0,0), (-1,-1),    'TOP'),
            ('ALIGN',          (0,0), (0,-1),     'RIGHT'),
            ('ALIGN',          (1,0), (1,-1),     'LEFT'),
            ('BOTTOMPADDING',  (0,0), (-1,-1),    6),
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 12))

        # --- Tabla de detalles con wrap activo ---
        detalle_table = Table(
            detalle_data,
            colWidths=[60, 80, 180, 80, 80],
            repeatRows=1
        )
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),   (-1,0),    colors.gray),
            ('TEXTCOLOR',   (0,0),   (-1,0),    colors.whitesmoke),
            ('FONTNAME',    (0,0),   (-1,0),    'Helvetica-Bold'),
            ('ALIGN',       (0,0),   (-1,-1),   'CENTER'),
            ('VALIGN',      (2,1),   (2,-1),    'TOP'),
            ('ALIGN',       (2,1),   (2,-1),    'LEFT'),
            ('GRID',        (0,0),   (-1,-1),   0.5, colors.black),
        ]))
        elements.append(detalle_table)
        elements.append(Spacer(1, 12))

        # --- Tabla de totales ---
        totales_data = [
            ["Total Neto",    f"${format_currency(float(total_neto))}"],
            ["IVA (19%)",     f"${format_currency(float(iva))}"],
            ["Total Orden",   f"${format_currency(float(total_orden))}"],
        ]
        totales_table = Table(
            totales_data,
            colWidths=[400, 120],
            hAlign="RIGHT"
        )
        totales_table.setStyle(TableStyle([
            ('FONTNAME',      (0,0), (-1,-1),    'Helvetica'),
            ('FONTSIZE',      (0,0), (-1,-1),    10),
            ('ALIGN',         (0,0), (0,-1),     'RIGHT'),
            ('ALIGN',         (1,0), (1,-1),     'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1),    6),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(1, 24))

        # --- Sección de firmas ---
        firmas_data = [
            ["__________________________", "__________________________", "__________________________"],
            ["Firma Técnico",           "Firma Jefatura",          "Firma Bodeguero"],
        ]
        firmas_table = Table(
            firmas_data,
            colWidths=[180, 180, 180],
            hAlign="CENTER"
        )
        firmas_table.setStyle(TableStyle([
            ('ALIGN',          (0,0), (-1,1),    'CENTER'),
            ('BOTTOMPADDING',  (0,0), (-1,1),    12),
            ('TOPPADDING',     (0,0), (-1,1),    12),
        ]))
        elements.append(firmas_table)

        # Construir PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        return HttpResponse(pdf, content_type='application/pdf')