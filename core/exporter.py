
#Exportación de los contactos de la agenda a formato JSON y generación de reportes impresos en formato PDF utilizando la biblioteca fpdf2.


import json
import os
from datetime import datetime
from fpdf import FPDF

from core import RUTA_EXPORT_JSON, RUTA_EXPORT_PDF
from core.manager_contact import obtener_todos_los_contactos


class ReportePDF(FPDF):
    #Clase personalizada para el diseño del reporte en PDF con encabezado y pie de página

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(58, 90, 120)  # Azul acento (#3a5a78)
        self.cell(0, 10, "Agenda de Contactos - Reporte General", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 10)
        self.set_text_color(110, 110, 110)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(0, 6, f"Generado el: {fecha_actual}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")


def exportar_json(ruta_salida: str = RUTA_EXPORT_JSON) -> str:
    
    #Exporta todos los contactos actuales a un archivo JSON con formato legible y devuelve la ruta absoluta del archivo generado
    
    directorio = os.path.dirname(ruta_salida)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    contactos = obtener_todos_los_contactos()

    # Ordenar contactos por ID
    contactos.sort(key=lambda c: c.get("id", 0))

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(contactos, f, indent=4, ensure_ascii=False)

    return os.path.abspath(ruta_salida)


def generar_pdf(ruta_json: str, ruta_pdf: str = RUTA_EXPORT_PDF) -> str:
  
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {ruta_json}")

    with open(ruta_json, "r", encoding="utf-8") as f:
        contactos = json.load(f)

    directorio = os.path.dirname(ruta_pdf)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    pdf = ReportePDF(orientation="P", unit="mm", format="Letter")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Resumen de registros
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, f"Total de contactos registrados: {len(contactos)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Anchos de columna que suman 196 mm
    anchos = [14, 48, 30, 58, 46]
    columnas = ["ID", "Nombre", "Teléfono", "Correo", "Ciudad"]

    # Encabezado de la tabla
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(58, 90, 120)  # Azul acento
    pdf.set_text_color(255, 255, 255)
    for col, ancho in zip(columnas, anchos):
        pdf.cell(ancho, 8, col, border=1, align="C", fill=True)
    pdf.ln()

    # Filas de la tabla con alternancia de colores (zebra striping)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)

    color_fondo_par = (244, 246, 248)
    color_fondo_impar = (255, 255, 255)

    for i, c in enumerate(contactos):
        fondo = color_fondo_par if i % 2 == 1 else color_fondo_impar
        pdf.set_fill_color(*fondo)

        pdf.cell(anchos[0], 7, str(c.get("id", "")), border=1, align="C", fill=True)
        pdf.cell(anchos[1], 7, str(c.get("nombre", "")), border=1, align="L", fill=True)
        pdf.cell(anchos[2], 7, str(c.get("telefono", "")), border=1, align="C", fill=True)
        pdf.cell(anchos[3], 7, str(c.get("correo", "")), border=1, align="L", fill=True)
        pdf.cell(anchos[4], 7, str(c.get("ciudad", "")), border=1, align="L", fill=True)
        pdf.ln()

    pdf.output(ruta_pdf)
    return os.path.abspath(ruta_pdf)
