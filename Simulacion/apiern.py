import requests
import json
from json.decoder import JSONDecodeError
import wget
import os
from ssspi.models import Simulaciones, ArchivoTMY
from django.core.files import File

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def consultar_api(latitud, longitud, simulacion_id):
    url = "https://api.minenergia.cl/api/proxy"

    payload = json.dumps({
        "action": {
            "action": "series",
            "interval": "hour",
            "stat": "mean",
            "tmy": True
        },
        "period": {
            "start": "2010-01-01",
            "end": "2016-12-31"
        },
        "export": {
            "label": "tmy",
            "format": "csv"
        },
        "variables": [
            {
                "id": "tempc",
                "options": {
                    "label": "Temp",
                    "stat": "default",
                    "recon": "on"
                }
            },
            {
                "id": "ghi",
                "options": {
                    "label": "GHI",
                    "stat": "default",
                    "band": "full",
                    "clearsky": False,
                    "fill_missing": False
                }
            }
        ],
        "position": [
            {
                "label": "S1",
                "type": "point",
                "lon": longitud,
                "lat": latitud
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        # Reemplazar por el Token entregado por exploradores incluyendo la palabra Token al inicio
        'Authorization': 'Token 0e752ad901b1ad52ff50378f92c429adcca1ec50'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        response_dict = response.json()
    except JSONDecodeError:
        print('La respuesta no pudo serializarse')
        return

    response_url = response_dict.get('url')

    archivo_ruta = os.path.join(BASE_DIR, 'TMY_Simulaciones')
    os.makedirs(archivo_ruta, exist_ok=True)

    nombre_archivo = f'TMY-SIM-{simulacion_id}.csv'
    archivo_ruta = os.path.join(archivo_ruta, nombre_archivo)

    wget.download(response_url, archivo_ruta)

    simulacion = FormSim.objects.get(id=simulacion_id)
    archivo_tmy = ArchivoTMY(simulacion=simulacion)

    with open(archivo_ruta, 'rb') as archivo:
        archivo_tmy.archivo.save(nombre_archivo, File(archivo))

    archivo_tmy.save()
         
    
