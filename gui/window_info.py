#Info del archivo

"""
info_window.py
--------------
Ventana "Información del archivo": muestra tamaño, fecha de última
modificación y permisos de lectura/escritura del archivo de contactos.
Los datos los entrega core.info_archivo.obtener_info() (os.stat y os.access).
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from core.info_archivo import obtener_info
from gui.mensajes import mostrar_error


def _formatear_fecha(valor):
    """Acepta un timestamp (st_mtime), un datetime o un texto ya formateado."""
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor).strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M:%S")
    return str(valor)


def _si_no(valor):
    return "Sí" if valor else "No"


class InfoWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Información del archivo")
        self.geometry("480x280")
        self.resizable(False, False)

        contenedor = ttk.Frame(self, padding=20)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Información del archivo de contactos",
                  font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self.variables = {}
        filas = [
            ("ruta", "Archivo:"),
            ("tamano", "Tamaño:"),
            ("modificado", "Última modificación:"),
            ("lectura", "Permiso de lectura:"),
            ("escritura", "Permiso de escritura:"),
        ]
        for indice, (clave, etiqueta) in enumerate(filas, start=1):
            ttk.Label(contenedor, text=etiqueta).grid(row=indice, column=0, sticky="w", pady=4, padx=(0, 15))
            self.variables[clave] = tk.StringVar(value="-")
            ttk.Label(contenedor, textvariable=self.variables[clave]).grid(row=indice, column=1, sticky="w", pady=4)

        botones = ttk.Frame(contenedor)
        botones.grid(row=len(filas) + 1, column=0, columnspan=2, pady=(20, 0), sticky="w")
        ttk.Button(botones, text="Actualizar", command=self._refrescar).pack(side="left", padx=(0, 10))
        ttk.Button(botones, text="Cerrar", command=self.destroy).pack(side="left")

        # Primera carga: si falla (archivo ausente, sin permisos...) se avisa y se cierra.
        if not self._refrescar():
            self.destroy()

    def _refrescar(self) -> bool:
        try:
            info = obtener_info()
        except Exception as error:
            mostrar_error(error, "Información del archivo", parent=self.master)
            return False

        tamano = info.get("tamano", 0)
        self.variables["ruta"].set(info.get("ruta", "-"))
        self.variables["tamano"].set(f"{tamano:,} bytes ({tamano / 1024:.2f} KB)")
        self.variables["modificado"].set(_formatear_fecha(info.get("modificado", "-")))
        self.variables["lectura"].set(_si_no(info.get("lectura")))
        self.variables["escritura"].set(_si_no(info.get("escritura")))
        return True