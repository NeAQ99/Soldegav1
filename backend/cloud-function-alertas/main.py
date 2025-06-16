# cloud-function-alertas/main.py
import requests

def trigger_alertas(request):
    url = "https://soldega-prod.rj.r.appspot.com/api/bodega/generar_alertas_programadas/"
    try:
        response = requests.post(url)
        print(f"🔁 Enviando solicitud a: {url}")
        print(f"📡 Código de respuesta: {response.status_code}")
        print(f"📦 Contenido: {response.text}")
        return f"Response: {response.status_code} - {response.text}"
    except Exception as e:
        print(f"❌ Error al ejecutar la función: {e}")
        return f"Error: {e}"
