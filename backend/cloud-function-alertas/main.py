import requests

def trigger_alertas(request):
    url = "https://soldega-prod.rj.r.appspot.com/api/bodega/generar_alertas_programadas/"
    try:
        response = requests.post(url)
        return f"Alerta ejecutada: {response.status_code} - {response.text}", response.status_code
    except Exception as e:
        return f"Error al ejecutar alerta: {str(e)}", 500
