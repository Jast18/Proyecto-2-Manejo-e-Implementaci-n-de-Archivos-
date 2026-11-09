
#Generación de copias de seguridad de la agenda en un archivo ZIP (backup.zip).
#Empaqueta contact.dat, index.json y contacts.sha256, y calcula el tamaño original frente al tamaño comprimido para determinar la tasa de compresión.


import os
import zipfile
from core import RUTA_DAT, RUTA_INDICE, RUTA_SHA, RUTA_RESPALDO_ZIP


def crear_respaldo(ruta_salida: str = RUTA_RESPALDO_ZIP) -> dict:
    
    #Crea un archivo ZIP con los datos esenciales de la agenda: contact.dat, index.json y contacts.sha256

  
    directorio_salida = os.path.dirname(ruta_salida)
    if directorio_salida:
        os.makedirs(directorio_salida, exist_ok=True)

    archivos_candidatos = [RUTA_DAT, RUTA_INDICE, RUTA_SHA]
    archivos_existentes = [f for f in archivos_candidatos if os.path.exists(f)]

    if not archivos_existentes:
        raise FileNotFoundError("No se encontraron archivos de datos para respaldar.")

    tamano_original = sum(os.path.getsize(f) for f in archivos_existentes)

    with zipfile.ZipFile(ruta_salida, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in archivos_existentes:
            nombre_archivo = os.path.basename(f)
            zf.write(f, arcname=nombre_archivo)

    tamano_comprimido = os.path.getsize(ruta_salida)

    return {
        "ruta": os.path.abspath(ruta_salida),
        "tamano_original": tamano_original,
        "tamano_comprimido": tamano_comprimido,
    }
