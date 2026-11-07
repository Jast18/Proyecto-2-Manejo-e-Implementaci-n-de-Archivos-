# Agenda de Contactos con Acceso Aleatorio

Laboratorio No. 2 — Manejo e Implementación de Archivos.

Aplicación de escritorio en Python (Tkinter) que administra una agenda de
contactos en un archivo de **registros de tamaño fijo**, con acceso aleatorio
mediante `seek()` / `tell()`, índice primario en JSON, verificación de
integridad SHA-256, respaldo ZIP y exportación a JSON y PDF.

## Cómo ejecutar

```bash
pip install -r requirements.txt   # instala fpdf2
python3 main.py                   # ejecutar siempre desde la raíz del proyecto
```

## Estructura

```
main.py                  punto de entrada
core/                    lógica de archivos (toda la práctica)
  registro.py            formato del registro de tamaño fijo
  contactos_manager.py   agregar, buscar por id, modificar (seek/tell)
  indice.py              indice.json (id -> número de registro)
  integridad.py          SHA-256 de contactos.dat
  respaldo.py            respaldo ZIP
  exportador.py          exportación a JSON y reporte PDF
  info_archivo.py        metadatos y permisos (os.stat / os.access)
gui/                     interfaz (no toca archivos)
  main_window.py         ventana principal y menú
  contactos_window.py    agregar / buscar / modificar
  info_window.py         información del archivo
  mensajes.py            traducción de errores a mensajes para el usuario
data/                    contactos.dat, indice.json, contactos.sha256
exports/                 contactos.json, reporte PDF
backups/                 respaldo ZIP
docs/                    documento PDF de la entrega
```

## Estructura del registro

> Completar con los largos definidos en `core/registro.py`.

| Campo    | Largo (bytes) |
|----------|---------------|
| id       | ?             |
| nombre   | ?             |
| teléfono | ?             |
| correo   | ?             |
| ciudad   | ?             |
| **Total**| ?             |

## Contrato entre `gui/` y `core/`

La interfaz solo llama a estas funciones. Si cambias un nombre o un valor de
retorno en `core/`, hay que ajustarlo también en `gui/`.

| Módulo | Función | Devuelve | Errores esperados |
|---|---|---|---|
| `core.contactos_manager` | `agregar_contacto(contacto)` | `{"registro": int, "posicion": int}` | `ValueError` (id duplicado o dato inválido) |
| `core.contactos_manager` | `buscar_por_id(id)` | `(contacto, {"registro": int, "posicion": int})` | `KeyError` si el id no existe |
| `core.contactos_manager` | `modificar_contacto(id, nuevos_datos)` | `{"registro": int, "posicion": int}` | `KeyError` si el id no existe |
| `core.integridad` | `verificar_integridad()` | `(bool, str)` — coincide / mensaje | — |
| `core.respaldo` | `crear_respaldo()` | `{"ruta": str, "tamano_original": int, "tamano_comprimido": int}` | — |
| `core.exportador` | `exportar_json()` | ruta del JSON (`str`) | — |
| `core.exportador` | `generar_pdf(ruta_json)` | ruta del PDF (`str`) | — |
| `core.info_archivo` | `obtener_info()` | `{"ruta", "tamano", "modificado", "lectura", "escritura"}` | — |

Notas del contrato:

- `contacto` es un diccionario con las claves `id` (int), `nombre`, `telefono`, `correo`, `ciudad`.
- `posicion` es el valor de `tell()` justo después del `seek()` al registro.
- `modificado` puede ser un timestamp (`st_mtime`) o un texto ya formateado.
- Cualquier excepción de archivo (`PermissionError`, `FileNotFoundError`, `OSError`, `json.JSONDecodeError`) que escape de `core/` es capturada por la interfaz y mostrada como aviso, sin cerrar la aplicación.