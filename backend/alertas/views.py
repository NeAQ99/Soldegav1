# alertas/views.py
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Alerta
from .serializers import AlertaSerializer

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all().order_by('-fecha_creacion')
    serializer_class = AlertaSerializer

    def list(self, request, *args, **kwargs):
        # Permite filtrar alertas por fecha mediante query params
        queryset = self.get_queryset()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(fecha_creacion__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha_creacion__lte=end_date)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Acción para resolver (aprobar o rechazar) una alerta
    @action(detail=True, methods=['patch'])
    def resolver(self, request, pk=None):
        alerta = self.get_object()
        # Solo permiten actualizar si el usuario tiene rol técnico, supervisor o secretario técnico
        if not hasattr(request.user, 'rol') or request.user.rol not in ['tecnico', 'supervisor', 'secretario tecnico']:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        nuevo_estado = request.data.get('estado')
        comentario = request.data.get('comentario', '')
        if nuevo_estado not in ['resuelta', 'rechazada']:
            return Response({"error": "Estado no válido"}, status=status.HTTP_400_BAD_REQUEST)
        alerta.estado = nuevo_estado
        alerta.comentario_resolucion = comentario
        alerta.fecha_resolucion = datetime.now()
        alerta.resuelta_por = request.user
        alerta.save()
        serializer = self.get_serializer(alerta)
        return Response(serializer.data)
