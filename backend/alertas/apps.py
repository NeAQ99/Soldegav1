# alertas/apps.py
import sys
from django.apps import AppConfig
from django.db import connections, ProgrammingError

class AlertasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alertas'

    def ready(self):
        # Evitar programar tareas durante comandos de migración o makemigrations
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        try:
            # Verificar si la tabla django_q_schedule ya existe.
            # Esto es PostgreSQL específico; si usas otro motor, deberás adaptar la consulta.
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT to_regclass('django_q_schedule')")
                result = cursor.fetchone()
            # Si la tabla existe, proceder a programar las tareas
            if result and result[0]:
                from django_q.tasks import schedule
                import alertas.tasks  # Asegúrate de que este módulo exista y contenga tus tareas

                schedule(
                    'alertas.tasks.revisar_ordenes_inactivas',
                    schedule_type='D'  # Ejecuta diariamente
                )
                schedule(
                    'alertas.tasks.revisar_solicitudes_inactivas',
                    schedule_type='D'
                )
                schedule(
                    'alertas.tasks.revisar_stock_bajo',
                    schedule_type='D'
                )
        except ProgrammingError:
            # Si ocurre un error (por ejemplo, la tabla aún no existe), se omite el scheduling.
            pass
