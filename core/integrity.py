
#Cálculo, almacenamiento y verificación de la integridad del archivo contact.dat utilizando el algoritmo SHA-256 (contacts.sha256).


import hashlib
import os
from core import RUTA_DAT, RUTA_SHA


def calcular_hash(ruta: str = RUTA_DAT) -> str:
    #Calcula el hash SHA-256 del archivo dado leyendo por bloques de 64 KB.
    #Si el archivo no existe, devuelve una cadena vacía.
    if not os.path.exists(ruta):
        return ""

    hasher = hashlib.sha256()
    with open(ruta, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def guardar_hash(ruta_dat: str = RUTA_DAT, ruta_sha: str = RUTA_SHA) -> str:

    #Calcula el SHA-256 actual de contact.dat y lo escribe en el archivo .sha256.
    #Devuelve el hash generado.
    
    directorio = os.path.dirname(ruta_sha)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    hash_valor = calcular_hash(ruta_dat)
    with open(ruta_sha, "w", encoding="utf-8") as f:
        f.write(hash_valor)
    return hash_valor


def verificar_integridad(ruta_dat: str = RUTA_DAT, ruta_sha: str = RUTA_SHA) -> tuple[bool, str]:
    
    #Verifica si el hash SHA-256 actual de contact.dat coincide con el almacenado en contacts.sha256.

    #Devuelve: (coincide: bool, mensaje: str)
    
    if not os.path.exists(ruta_dat):
        directorio = os.path.dirname(ruta_dat)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        open(ruta_dat, "wb").close()
        h = guardar_hash(ruta_dat, ruta_sha)
        return True, f"Archivo de contactos inicializado (vacío). SHA-256: {h[:10]}..."

    if not os.path.exists(ruta_sha) or os.path.getsize(ruta_sha) == 0:
        h = guardar_hash(ruta_dat, ruta_sha)
        return True, f"Hash SHA-256 inicial calculado y guardado: {h[:10]}..."

    hash_actual = calcular_hash(ruta_dat)
    with open(ruta_sha, "r", encoding="utf-8") as f:
        hash_guardado = f.read().strip()

    if hash_actual.lower() == hash_guardado.lower():
        return True, f"El hash coincide ({hash_actual[:10]}...). El archivo no ha sido alterado."
    else:
        return (
            False,
            f"El hash esperado ({hash_guardado[:10]}...) no coincide con el actual ({hash_actual[:10]}...). "
            f"El archivo pudo haber sido modificado externamente."
        )
