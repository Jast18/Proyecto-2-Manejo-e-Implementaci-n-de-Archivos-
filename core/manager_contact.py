
#Administración del archivo de registros de tamaño fijo contact.dat.
#Func: Agregar, buscar y modificar contactos utilizando acceso aleatorio (seek/tell)
#índice primario (index.json), verificador de integridad (SHA-256).


import os
from core import RUTA_DAT
from core.record import TAMANO_REGISTRO, empaquetar_registro, desempaquetar_registro
from core.index import cargar_indice, guardar_indice
from core.integrity import guardar_hash


def _asegurar_archivo_datos():
    """Crea el directorio y el archivo contact.dat si no existen."""
    directorio = os.path.dirname(RUTA_DAT)
    if directorio:
        os.makedirs(directorio, exist_ok=True)
    if not os.path.exists(RUTA_DAT):
        open(RUTA_DAT, "wb").close()
        guardar_hash()


def agregar_contacto(contacto: dict) -> dict:

    #Agrega un nuevo contacto al final del archivo contact.dat.
    #Actualiza el índice en JSON y recalcula el hash SHA-256.

    try:
        id_contacto = int(contacto["id"])
    except (KeyError, ValueError, TypeError):
        raise ValueError("El ID debe ser un número entero.")

    if id_contacto <= 0:
        raise ValueError("El ID debe ser un entero positivo.")

    nombre = contacto.get("nombre", "").strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")

    _asegurar_archivo_datos()
    indice = cargar_indice()

    if id_contacto in indice:
        raise ValueError(f"El ID {id_contacto} ya existe en la agenda.")

    # El nuevo registro se agrega al final del archivo
    tamano_archivo = os.path.getsize(RUTA_DAT)
    num_registro = tamano_archivo // TAMANO_REGISTRO
    offset = num_registro * TAMANO_REGISTRO

    datos_bytes = empaquetar_registro(contacto)

    with open(RUTA_DAT, "r+b") as f:
        f.seek(offset)
        posicion = f.tell()
        f.write(datos_bytes)
        f.flush()

    # Actualizar índice y hash de integridad
    indice[id_contacto] = num_registro
    guardar_indice(indice)
    guardar_hash()

    return {"registro": num_registro, "posicion": posicion}


def buscar_por_id(id_contacto: int) -> tuple[dict, dict]:

    #Busca contacto por su ID utilizando el índice JSON y acceso aleatorio (seek/tell).

    #Devuelve:(contacto: dict, {"registro": int, "posicion": int})

    #Lanza:KeyError: Si el ID no existe en el índice.
    
    try:
        id_val = int(id_contacto)
    except (ValueError, TypeError):
        raise ValueError("El ID debe ser un número entero.")

    indice = cargar_indice()
    if id_val not in indice:
        raise KeyError(f"No existe un contacto con el ID {id_val}.")

    num_registro = indice[id_val]
    offset = num_registro * TAMANO_REGISTRO

    _asegurar_archivo_datos()
    with open(RUTA_DAT, "rb") as f:
        f.seek(offset)
        posicion = f.tell()
        chunk = f.read(TAMANO_REGISTRO)

    if len(chunk) < TAMANO_REGISTRO:
        raise OSError(f"Registro incompleto en la posición {posicion} (se esperaban {TAMANO_REGISTRO} bytes).")

    contacto = desempaquetar_registro(chunk)
    return contacto, {"registro": num_registro, "posicion": posicion}


def modificar_contacto(id_contacto: int, nuevos_datos: dict) -> dict:
    #Modifica un contacto existente sobrescribiendo exactamente sus 150 bytes en contact.dat usando seek() y tell().

    #Devuelve: {"registro": int, "posicion": int}

    #Lanza: KeyError: Si el ID no existe o ValueError: Si los datos son inválidos.

    try:
        id_val = int(id_contacto)
    except (ValueError, TypeError):
        raise ValueError("El ID debe ser un número entero.")

    indice = cargar_indice()
    if id_val not in indice:
        raise KeyError(f"No existe un contacto con el ID {id_val}.")

    num_registro = indice[id_val]
    offset = num_registro * TAMANO_REGISTRO

    # Conservar el ID original inalterado
    contacto_completo = {"id": id_val, **nuevos_datos}
    nombre = contacto_completo.get("nombre", "").strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio.")

    datos_bytes = empaquetar_registro(contacto_completo)

    _asegurar_archivo_datos()
    with open(RUTA_DAT, "r+b") as f:
        f.seek(offset)
        posicion = f.tell()
        f.write(datos_bytes)
        f.flush()

    # Actualizar hash de integridad
    guardar_hash()

    return {"registro": num_registro, "posicion": posicion}


def obtener_todos_los_contactos() -> list[dict]:
    
    #Lee secuencialmente todos los registros válidos de contact.dat.
    #Devuelve una lista de diccionarios con cada contacto.
    
    if not os.path.exists(RUTA_DAT):
        return []

    contactos = []
    with open(RUTA_DAT, "rb") as f:
        while True:
            chunk = f.read(TAMANO_REGISTRO)
            if len(chunk) < TAMANO_REGISTRO:
                break
            contactos.append(desempaquetar_registro(chunk))

    return contactos
