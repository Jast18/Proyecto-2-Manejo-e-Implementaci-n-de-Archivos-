
#Estructura y empaquetado/desempaquetado de registros de tamaño fijo.

#Estructura de cada registro:
#id: 4 bytes  (entero con signo, big-endian: >i)
#nombre: 50 bytes (cadena UTF-8 terminada o rellenada en nulos)
#teléfono: 16 bytes (cadena UTF-8)
#correo: 50 bytes (cadena UTF-8)
#ciudad: 30 bytes (cadena UTF-8)
#Total:  150 bytes


import struct

ID_LEN = 4
NOMBRE_LEN = 50
TELEFONO_LEN = 16
CORREO_LEN = 50
CIUDAD_LEN = 30

TAMANO_REGISTRO = ID_LEN + NOMBRE_LEN + TELEFONO_LEN + CORREO_LEN + CIUDAD_LEN  # 150 bytes
FORMATO = f">i{NOMBRE_LEN}s{TELEFONO_LEN}s{CORREO_LEN}s{CIUDAD_LEN}s"


def _ajustar_campo(texto: str, largo: int) -> bytes:

    #Convierte una cadena a bytes UTF-8 asegurando que no exceda 'largo' bytes
    #y sin cortar caracteres multibyte a la mitad.

    raw = (texto or "").strip().encode("utf-8")
    if len(raw) > largo:
        raw = raw[:largo].decode("utf-8", errors="ignore").encode("utf-8")
    return raw


def _decodificar_campo(campo_bytes: bytes) -> str:

    #Toma los bytes de un campo, corta en el primer byte nulo (\x00) y decodifica UTF-8.
    
    return campo_bytes.split(b"\x00", 1)[0].decode("utf-8", errors="replace").strip()


def empaquetar_registro(contacto: dict) -> bytes:
    #Convierte un diccionario de contacto en una secuencia de exactamente 150 bytes.
    #El diccionario debe tener: id (int), nombre, telefono, correo, ciudad.

    try:
        id_val = int(contacto["id"])
    except (KeyError, ValueError, TypeError) as err:
        raise ValueError(f"El ID del contacto debe ser un número entero válido: {err}")

    nom_bytes = _ajustar_campo(contacto.get("nombre", ""), NOMBRE_LEN)
    tel_bytes = _ajustar_campo(contacto.get("telefono", ""), TELEFONO_LEN)
    cor_bytes = _ajustar_campo(contacto.get("correo", ""), CORREO_LEN)
    ciu_bytes = _ajustar_campo(contacto.get("ciudad", ""), CIUDAD_LEN)

    return struct.pack(FORMATO, id_val, nom_bytes, tel_bytes, cor_bytes, ciu_bytes)


def desempaquetar_registro(datos: bytes) -> dict:
    #Convierte una secuencia de 150 bytes en un diccionario con los datos del contacto.

    if len(datos) != TAMANO_REGISTRO:
        raise ValueError(
            f"Tamaño de registro inválido: se esperaban {TAMANO_REGISTRO} bytes, "
            f"pero se recibieron {len(datos)} bytes."
        )

    id_val, nom_b, tel_b, cor_b, ciu_b = struct.unpack(FORMATO, datos)

    return {
        "id": id_val,
        "nombre": _decodificar_campo(nom_b),
        "telefono": _decodificar_campo(tel_b),
        "correo": _decodificar_campo(cor_b),
        "ciudad": _decodificar_campo(ciu_b),
    }
