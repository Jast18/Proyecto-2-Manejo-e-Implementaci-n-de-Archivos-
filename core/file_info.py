
#Consulta de metadatos y permisos del archivo contact.dat utilizando las funciones os.stat y os.access de la biblioteca estándar de Python.


import os
from core import RUTA_DAT


def obtener_info(ruta: str = RUTA_DAT) -> dict:
    
    #Obtiene los metadatos y permisos del archivo de contactos. Si el archivo no existe, lo crea vacío para permitir la consulta.

    #Devuelve un diccionario con las claves
    
    directorio = os.path.dirname(ruta)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    if not os.path.exists(ruta):
        open(ruta, "wb").close()

    estadisticas = os.stat(ruta)

    return {
        "ruta": os.path.abspath(ruta),
        "tamano": estadisticas.st_size,
        "modificado": estadisticas.st_mtime,
        "lectura": os.access(ruta, os.R_OK),
        "escritura": os.access(ruta, os.W_OK),
    }
