
#Administración del índice primario en formato JSON (index.json).
#Mapea el identificador único (ID) del contacto al número de registro en el archivo de datos.


import json
import os
from core import RUTA_INDICE


def cargar_indice(ruta: str = RUTA_INDICE) -> dict[int, int]:
    
    #Carga el índice desde el archivo JSON.
    #Devuelve un diccionario donde las claves son IDs (int) y los valores son los números de registro (int, base 0).
    #Si el archivo no existe o está vacío, devuelve un diccionario vacío {}.
    
    if not os.path.exists(ruta):
        return {}

    if os.path.getsize(ruta) == 0:
        return {}

    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return {}
        datos = json.loads(contenido)

    return {int(k): int(v) for k, v in datos.items()}


def guardar_indice(indice: dict[int, int], ruta: str = RUTA_INDICE) -> None:
    
    #Guarda el índice en el archivo JSON especificado y las claves numéricas se ordenan ascendentemente para mantener legibilidad.
    
    directorio = os.path.dirname(ruta)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    datos_para_guardar = {
        str(k): int(v)
        for k, v in sorted(indice.items(), key=lambda item: int(item[0]))
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos_para_guardar, f, indent=2, ensure_ascii=False)
