import io
from datetime import datetime,timedelta
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

from ordenes.models import OrdenesCompras
from .models import Proveedor, Solicitud, OrdenesCompras, OrdenCompraDetalle
from .serializers import (
    ProveedorSerializer,
    SolicitudSerializer,
    OrdenesComprasSerializer,
    OrdenCompraDetalleSerializer,
)

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by('nombre_proveedor')
    serializer_class = ProveedorSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all().order_by('-fecha_creacion')
    serializer_class = SolicitudSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_creador=self.request.user)

    # Acción para aprobar la solicitud (supervisor y técnico)
    @action(detail=True, methods=['patch'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        # Permitir aprobación si el rol es 'supervisor' o 'tecnico'
        if not hasattr(request.user, 'rol') or request.user.rol not in ['supervisor', 'tecnico']:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        solicitud.estado = 'aprobada'
        solicitud.save()
        return Response({"status": "Solicitud aprobada"})

    # Acción para rechazar la solicitud (supervisor y técnico)
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
    Endpoint para generar el PDF de una Solicitud de Compra de Materiales e Insumos (vertical).
    Se espera recibir el parámetro 'solicitud_id' en la query string.
    
    Mejoras:
      - Se incluye el número de Folio (ingresado manualmente) en la esquina superior derecha, en tamaño grande.
      - Se elimina "Stock en Bodega" de la cabecera (se mostrará en la tabla de detalles para cada ítem).
      - Se muestran Fecha, Solicitante y Usuario Creador en una tabla separada debajo del encabezado.
      - Se agrega el logo en la esquina superior izquierda.
      - La tabla de detalles muestra: Item, Cantidad, Insumo/Material Solicitado, Cargo y Stock Bodega.
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
        
        # Obtener detalles de la solicitud
        detalles = solicitud.detalles.all()
        detalle_header = ["Item", "Cantidad", "Insumo/Material Solicitado", "Cargo", "Stock Bodega"]
        if detalles.exists():
            detalle_data = [detalle_header] + [
                [
                    str(idx + 1),
                    str(det.cantidad),
                    det.producto,
                    det.motivo,  # Se usa "motivo" para representar el cargo.
                    str(det.stock_bodega) if hasattr(det, 'stock_bodega') and det.stock_bodega is not None else ""
                ] for idx, det in enumerate(detalles)
            ]
        else:
            detalle_data = [detalle_header, ["-", "-", "-", "-", "-"]]
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)  # Formato vertical
        styles = getSampleStyleSheet()
        elements = []

        # Intentar cargar el logo
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

        # Encabezado: Una tabla con dos columnas:
        # - Columna izquierda: Logo.
        # - Columna derecha: Folio en fuente grande y alineado a la derecha.
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
        
        # Tabla de información adicional (Fecha, Solicitante, Usuario Creador)
        info_data = [
            ["Fecha:", solicitud.fecha_creacion.strftime("%d/%m/%Y")],
            ["Solicitante:", solicitud.nombre_solicitante],
            ["Usuario Creador:", solicitud.usuario_creador.username if solicitud.usuario_creador else "n/a"],
        ]
        info_table = Table(info_data, colWidths=[120, 380])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 12))
        
        # Título del documento
        elements.append(Paragraph("Solicitud de Compra de Materiales e Insumos", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Tabla de detalles
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

        # Sección de Firmas
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
    queryset = OrdenesCompras.objects.all().order_by('-fecha')
    serializer_class = OrdenesComprasSerializer

    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """
        Devuelve las órdenes de compra con estado "pendiente" o "items pendientes".
        """
        pendientes_oc = self.get_queryset().filter(estado__in=['pendiente', 'items pendientes'])
        serializer = self.get_serializer(pendientes_oc, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # Calcular la fecha límite: 30 días atrás desde ahora
        thirty_days_ago = datetime.now() - timedelta(days=30)
        # Actualizar órdenes pendientes o producto pendiente a "inactiva" si su fecha es anterior a esa fecha
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
    """
    Endpoint para generar el PDF de una Orden de Compra.
    Se espera recibir el parámetro 'orden_id' en la query string.
    """
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        orden_id = request.query_params.get('orden_id')
        if not orden_id:
            return Response({"error": "Se requiere orden_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            orden = OrdenesCompras.objects.get(id=orden_id)
        except OrdenesCompras.DoesNotExist:
            return Response({"error": "Orden no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calcular totales
        detalles = orden.detalles.all()
        total_neto = sum([detalle.cantidad * detalle.precio_unitario for detalle in detalles])
        iva = total_neto * Decimal('0.19')
        total_orden = total_neto + iva

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # --- Encabezado: Logo en la esquina superior izquierda y datos de la empresa a la derecha ---
        logo_path = finders.find("images/logo.png")
        if logo_path:
            try:
                logo_element = Image(logo_path, width=100, height=50)
                logo_element.hAlign = 'LEFT'
            except Exception as e:
                print("Error cargando el logo:", e)
                logo_element = Paragraph("Logo no encontrado", styles['Normal'])
        else:
            print("Logo no encontrado en static/images/logo.png")
            logo_element = Paragraph("Logo no encontrado", styles['Normal'])
        company_details = (
            "Inversiones Imperia SpA<br/>"
            "52.001.387-3<br/>"
            "Bolivar #202<br/>"
            "Edificio Finanzas, Oficina #511"
        )
        company_paragraph = Paragraph(company_details, styles['Normal'])
        header_table = Table([[logo_element, company_paragraph]], colWidths=[150, 350])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))

        # --- Título del documento ---
        elements.append(Paragraph("Orden de Compra", styles['Title']))
        elements.append(Spacer(1, 12))

        # --- Encabezado de la orden reorganizado en 4 columnas ---
        # Cada fila contendrá dos pares etiqueta-valor para agrupar la información.
        orden_data = []
        orden_data.append([
            "N° Orden:", orden.numero_orden,
            "Fecha:", orden.fecha.strftime("%d/%m/%Y")
        ])
        orden_data.append([
            "N° Cotización:", orden.nro_cotizacion if getattr(orden, 'nro_cotizacion', None) else "n/a",
            "Empresa:", orden.empresa
        ])
        orden_data.append([
            "Merc. Puesta en:", orden.mercaderia_puesta_en if getattr(orden, 'mercaderia_puesta_en', None) else "n/a",
            "Proveedor:", orden.proveedor.nombre_proveedor if orden.proveedor else "n/a"
        ])
        orden_data.append([
            "Rut:", orden.proveedor.rut if orden.proveedor else "n/a",
            "Domicilio:", orden.proveedor.domicilio if orden.proveedor else "n/a"
        ])
        orden_data.append([
            "Ciudad:", orden.proveedor.ubicacion if orden.proveedor else "n/a",
            "", ""
        ])
        header_table_order = Table(orden_data, colWidths=[100, 150, 100, 150])
        # Se definen estilos para celdas específicas:
        header_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (0,0), colors.whitesmoke),   # "N° Orden:"
            ('BACKGROUND', (0,1), (0,1), colors.whitesmoke),   # "N° Cotización:"
            ('BACKGROUND', (0,2), (0,2), colors.whitesmoke),   # "Merc. Puesta en:"
            ('BACKGROUND', (0,3), (0,3), colors.whitesmoke),   # "Rut:"
            ('BACKGROUND', (0,4), (0,4), colors.whitesmoke),   # "Ciudad:"
            # Celdas de etiqueta que se mantienen en gris:
            ('BACKGROUND', (2,0), (2,0), colors.whitesmoke),     # "Fecha:"
            ('BACKGROUND', (2,1), (2,1), colors.whitesmoke),     # "Empresa:"
            ('BACKGROUND', (2,2), (2,2), colors.whitesmoke),     # "Proveedor:"
            ('BACKGROUND', (2,3), (2,3), colors.whitesmoke),     # "Domicilio:"
        ])
        header_table_order.setStyle(header_style)
        elements.append(header_table_order)
        elements.append(Spacer(1, 12))

        # --- Detalle de la Orden ---
        detalle_header = ["Cantidad", "Producto / Detalle", "Precio Unitario", "Total Producto"]
        detalle_data = [detalle_header]
        if detalles:
            for detalle in detalles:
                cantidad = detalle.cantidad
                producto = detalle.detalle  # Campo 'detalle'
                precio_unitario = detalle.precio_unitario
                total_producto = cantidad * precio_unitario
                detalle_data.append([
                    str(cantidad),
                    producto,
                    f"${precio_unitario:.2f}",
                    f"${total_producto:.2f}"
                ])
        else:
            detalle_data.append(["-", "No hay detalles", "-", "-"])
        detalle_table = Table(detalle_data, repeatRows=1)
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(detalle_table)
        elements.append(Spacer(1, 12))

        # --- Totales ---
        totales_data = [
            ["Total Neto:", f"${total_neto:.2f}"],
            ["IVA (19%):", f"${iva:.2f}"],
            ["Total Orden:", f"${total_orden:.2f}"],
        ]
        totales_table = Table(totales_data, colWidths=[150, 100], hAlign='RIGHT')
        totales_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(1, 12))

        # --- Información adicional ---
        additional_data = [
            ["Plazo de entrega:", orden.plazo_entrega],
            ["Forma de pago:", orden.forma_pago],
            ["Comentarios:", orden.comentarios or ""],
        ]
        additional_table = Table(additional_data, colWidths=[150, 300], hAlign='LEFT')
        additional_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(additional_table)
        elements.append(Spacer(1, 24))

        # --- Firmas ---
        firmas_data = [
            ["Jefe Faena", "Solicitante", "Contabilidad"],
            ["________________________", "________________________", "________________________"],
        ]
        firmas_table = Table(firmas_data, colWidths=[150, 150, 150], hAlign='CENTER')
        firmas_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('FONTSIZE', (0,1), (-1,1), 10),
            ('TOPPADDING', (0,1), (-1,1), 12),
        ]))
        elements.append(firmas_table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orden_compra.pdf"'
        response.write(pdf)
        return response
