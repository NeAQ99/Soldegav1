# movimientos/views.py
from datetime import datetime
import io
import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from django.db.models import Sum

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Entrada, Salida
from .serializers import EntradaSerializer, SalidaSerializer, EntradaCreateSerializer
from bodega.models import Producto
from ordenes.models import OrdenesCompras, OrdenCompraDetalle

logger = logging.getLogger(__name__)  # ✅ Bien definido aquí


class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return EntradaCreateSerializer
        return EntradaSerializer

    def get_queryset(self):
        qs = Entrada.objects.select_related('producto', 'usuario', 'orden_compra').order_by('-fecha')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            qs = qs.filter(fecha__date__gte=start_date, fecha__date__lte=end_date)

        consignacion_param = self.request.query_params.get('consignacion')
        if consignacion_param and consignacion_param.lower() == "true":
            qs = qs.filter(producto__consignacion=True)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entradas = serializer.save()
        # ahora usamos EntradaSerializer para serializar cada entrada creada
        return Response(EntradaSerializer(entradas, many=True).data, status=status.HTTP_201_CREATED)



class SalidaViewSet(viewsets.ModelViewSet):
    queryset = Salida.objects.all()
    serializer_class = SalidaSerializer

    def get_queryset(self):
        qs = Salida.objects.select_related('producto', 'usuario').order_by('-fecha')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            qs = qs.filter(fecha__date__gte=start_date, fecha__date__lte=end_date)
        consignacion_param = self.request.query_params.get('consignacion')
        if consignacion_param and consignacion_param.lower() == "true":
            qs = qs.filter(producto__consignacion=True)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data
        items = data.get('items', [])
        comentario = data.get('comentario', '')
        created_items = []

        for item in items:
            item['comentario'] = comentario
            serializer = self.get_serializer(data=item)
            serializer.is_valid(raise_exception=True)
            salida = serializer.save(usuario=request.user)
            created_items.append(serializer.data)
            try:
                product = Producto.objects.get(id=item.get('producto'))
                product.stock_actual -= int(item.get('cantidad'))
                product.save()
            except Producto.DoesNotExist:
                pass

        return Response(created_items, status=status.HTTP_201_CREATED)



def format_currency(value):
    s = "{:,.2f}".format(value)
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def format_currency(value):
    s = "{:,.2f}".format(value)
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

class ReportePDFView(viewsets.ViewSet):
    """
    Endpoint para generar el PDF del movimiento (entradas o salidas).
    Parámetros:
      - tipo: 'entrada' o 'salida'
      - start_date y end_date en formato YYYY-MM-DD
      - consignacion (opcional)
    """
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        tipo = request.query_params.get('tipo', 'entrada')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        consignacion_param = request.query_params.get('consignacion')

        if not start_date or not end_date:
            return Response({"error": "Se requieren start_date y end_date"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        if tipo == 'entrada':
            queryset = Entrada.objects.filter(
                fecha__date__gte=start.date(), 
                fecha__date__lte=end.date()
            )
            # Encabezado con dos columnas para producto: Código y Nombre
            header = ['Cantidad', 'Código Producto', 'Nombre Producto', 'Motivo / Orden', 'Valor Producto', 'Total Producto']
        else:
            queryset = Salida.objects.filter(
                fecha__date__gte=start.date(), 
                fecha__date__lte=end.date()
            )
            header = ['Cantidad', 'Código Producto', 'Nombre Producto', 'Cargo', 'Valor Producto', 'Total Producto']

        if consignacion_param and consignacion_param.lower() == "true":
            queryset = queryset.filter(producto__consignacion=True)

        total_movimientos = 0
        total_valor = 0
        data = [header]

        # Definir un estilo de párrafo para permitir que el texto se ajuste (wrap) en la celda
        stylesheet = getSampleStyleSheet()
        wrapStyle = ParagraphStyle(
            name='Wrap',
            fontSize=10,
            leading=12,
            wordWrap='CJK'  # Puedes ajustar según tus necesidades
        )

        if tipo == 'entrada':
            for entrada in queryset:
                cantidad = entrada.cantidad
                # Se espera que entrada.producto sea un objeto con atributos 'codigo' y 'nombre'
                codigo = entrada.producto.codigo if hasattr(entrada.producto, 'codigo') else ""
                nombre = entrada.producto.nombre if hasattr(entrada.producto, 'nombre') else ""
                if entrada.motivo == 'recepcion_oc' and entrada.orden_compra and entrada.orden_compra.numero_orden:
                    motivo_display = "OC " + entrada.orden_compra.numero_orden
                else:
                    motivo_display = entrada.motivo
                valor_producto = float(entrada.costo_unitario)
                total_producto = cantidad * valor_producto
                total_movimientos += cantidad
                total_valor += total_producto

                # Convertir el código y nombre a Paragraph para que se ajusten en la celda
                codigo_par = Paragraph(codigo, wrapStyle)
                nombre_par = Paragraph(nombre, wrapStyle)
                data.append([
                    str(cantidad),
                    codigo_par,
                    nombre_par,
                    motivo_display,
                    f"${format_currency(valor_producto)}",
                    f"${format_currency(total_producto)}"
                ])
            data.append(['', '', '', 'Total Entradas:', str(total_movimientos), f"${format_currency(total_valor)}"])
        else:
            for salida in queryset:
                cantidad = salida.cantidad
                codigo = salida.producto.codigo if hasattr(salida.producto, 'codigo') else ""
                nombre = salida.producto.nombre if hasattr(salida.producto, 'nombre') else ""
                cargo = salida.cargo
                valor_producto = float(salida.producto.precio_compra)
                total_producto = cantidad * valor_producto
                total_movimientos += cantidad
                total_valor += total_producto

                codigo_par = Paragraph(codigo, wrapStyle)
                nombre_par = Paragraph(nombre, wrapStyle)
                data.append([
                    str(cantidad),
                    codigo_par,
                    nombre_par,
                    cargo,
                    f"${format_currency(valor_producto)}",
                    f"${format_currency(total_producto)}"
                ])
            data.append(['', '', '', 'Total Salidas:', str(total_movimientos), f"${format_currency(total_valor)}"])

        # Inicializar el documento PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        title = Paragraph("Informe de Movimiento", stylesheet['Title'])
        elements.append(title)
        elements.append(Spacer(1, 40))

        # Definir anchos de columnas (ajústalos según tus necesidades)
        colWidths = [60, 80, 120, 100, 80, 80]
        table = Table(data, colWidths=colWidths)
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.orange),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="informe_movimiento.pdf"'
        response.write(pdf)
        return response