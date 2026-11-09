
#Módulo central de la aplicación para el manejo de archivos:
#- record: empaquetado y desempaquetado de registros de tamaño fijo
#- manager_contact: agregar, buscar y modificar registros con seek/tell
#- index: índice primario en JSON (ID -> número de registro)
#- integrity: cálculo y verificación de hash SHA-256
#- backup: generación de copias de seguridad en formato ZIP
#- exporter: exportación a JSON y generación de reportes en PDF
#- file_info: metadatos del archivo mediante os.stat y os.access


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUPS_DIR = BASE_DIR / "backups"

RUTA_DAT = str(DATA_DIR / "contact.dat")
RUTA_INDICE = str(DATA_DIR / "index.json")
RUTA_SHA = str(DATA_DIR / "contacts.sha256")
RUTA_EXPORT_JSON = str(EXPORTS_DIR / "contact.json")
RUTA_EXPORT_PDF = str(EXPORTS_DIR / "reporte.pdf")
RUTA_RESPALDO_ZIP = str(BACKUPS_DIR / "backup.zip")
