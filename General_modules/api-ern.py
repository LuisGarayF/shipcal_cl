import requests
import json
from json.decoder import JSONDecodeError
import wget
import os
from FE1.views import latitud, longitud

print(latitud,longitud)

# Consulta a API Exploradores Ministerio Energía

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
            #"lon": longitud,
            #"lat": latitud
            "lon": -70.66209250663925,
            "lat": -33.44859957333846
        }
    ]
})
headers = {
    'Content-Type': 'application/json',
    # Reemplazar por el Token entregado por exploradores incluyendo la palabra Token al inicio
    'Authorization': 'Token 0e752ad901b1ad52ff50378f92c429adcca1ec50'
}

response = requests.request("POST", url, headers=headers, data=payload)

# Manejador de errores
try:
    response_dict = response.json()
except JSONDecodeError:
    print('La respuesta no pudo serializarse')

# Guardando el archivo TMY en la carpeta API_ERN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file = BASE_DIR+"\General_modules\API_ERN\datos.csv"

#file = BASE_DIR+"\General_modules\API_ERN\datos.xlsx"

response_url = response_dict.get('url')

print(response_url)

wget.download(response_url, file)
