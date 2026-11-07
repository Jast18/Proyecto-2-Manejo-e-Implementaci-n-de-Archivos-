#Contactos, exportar, herramientas y ayuda

"""
main_window.py
--------------
Ventana principal. El menú tiene cuatro entradas:
  - Contactos   (funcional): agregar, buscar por ID, modificar
  - Exportar    (funcional): exportar a JSON, generar reporte PDF
  - Herramientas(funcional): verificar integridad, respaldo ZIP, información del archivo
  - Ayuda       (simulado)

En macOS, Tkinter coloca el menú en la barra superior del sistema (no dentro
de la ventana), por eso cada opción funcional tiene además un botón visible
en la ventana. Así la aplicación se puede usar sin depender de ese menú.

Esta capa no toca archivos: solo llama a las funciones de core/ y muestra
los resultados o los errores al usuario.
"""

import tkinter as tk
from tkinter import ttk, Menu, messagebox

from core.integridad import verificar_integridad
from core.respaldo import crear_respaldo
from core.exportador import exportar_json, generar_pdf
from gui.contactos_window import ContactosWindow
from gui.info_window import InfoWindow
from gui.mensajes import mostrar_error

COLOR_ACENTO = "#3a5a78"
COLOR_FONDO = "#f4f6f8"


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda de Contactos")
        self.geometry("640x500")
        self.configure(bg=COLOR_FONDO)

        self._ventana_contactos = None

        self._configurar_estilo()
        self._construir_menu()
        self._construir_contenido()

        # La verificación inicial se hace con la ventana ya visible, así un
        # aviso de archivo alterado aparece sobre la aplicación y no antes.
        self.after(300, self._verificar_al_iniciar)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _configurar_estilo(self):
        # El tema 'clam' respeta los colores personalizados también en macOS
        # (los botones nativos de Aqua los ignoran).
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO, font=("Arial", 11))
        estilo.configure("TLabelframe", background=COLOR_FONDO)
        estilo.configure("TLabelframe.Label", background=COLOR_FONDO, foreground=COLOR_ACENTO,
                         font=("Arial", 11, "bold"))
        estilo.configure("TButton", font=("Arial", 10), padding=6)
        estilo.configure("Accent.TButton", font=("Arial", 10, "bold"), foreground="white",
                         background=COLOR_ACENTO, padding=8)
        estilo.map("Accent.TButton", background=[("active", "#2c4459")])

    def _construir_menu(self):
        barra = Menu(self)

        menu_contactos = Menu(barra, tearoff=0)
        menu_contactos.add_command(label="Agregar", command=lambda: self._abrir_contactos(0))
        menu_contactos.add_command(label="Buscar por ID", command=lambda: self._abrir_contactos(1))
        menu_contactos.add_command(label="Modificar", command=lambda: self._abrir_contactos(2))
        barra.add_cascade(label="Contactos", menu=menu_contactos)

        menu_exportar = Menu(barra, tearoff=0)
        menu_exportar.add_command(label="Exportar a JSON", command=self._exportar_json)
        menu_exportar.add_command(label="Generar reporte PDF", command=self._generar_pdf)
        barra.add_cascade(label="Exportar", menu=menu_exportar)

        menu_herramientas = Menu(barra, tearoff=0)
        menu_herramientas.add_command(label="Verificar integridad", command=self._verificar_integridad)
        menu_herramientas.add_command(label="Crear respaldo ZIP", command=self._crear_respaldo)
        menu_herramientas.add_command(label="Información del archivo", command=self._abrir_info)
        barra.add_cascade(label="Herramientas", menu=menu_herramientas)

        menu_ayuda = Menu(barra, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self._ayuda_simulada)
        menu_ayuda.add_command(label="Manual de usuario", command=self._ayuda_simulada)
        barra.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.config(menu=barra)

    def _construir_contenido(self):
        contenedor = ttk.Frame(self, padding=25)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Agenda de Contactos", font=("Arial", 20, "bold"),
                  foreground=COLOR_ACENTO).pack(anchor="w")
        ttk.Label(contenedor, text="Registros de tamaño fijo con acceso aleatorio",
                  foreground="#666666").pack(anchor="w", pady=(0, 15))

        self._grupo(contenedor, "Contactos", [
            ("Agregar", lambda: self._abrir_contactos(0)),
            ("Buscar por ID", lambda: self._abrir_contactos(1)),
            ("Modificar", lambda: self._abrir_contactos(2)),
        ])
        self._grupo(contenedor, "Exportar", [
            ("Exportar a JSON", self._exportar_json),
            ("Generar reporte PDF", self._generar_pdf),
        ])
        self._grupo(contenedor, "Herramientas", [
            ("Verificar integridad", self._verificar_integridad),
            ("Crear respaldo ZIP", self._crear_respaldo),
            ("Información del archivo", self._abrir_info),
        ])

        self.var_estado = tk.StringVar(value="Integridad del archivo: verificando...")
        ttk.Label(contenedor, textvariable=self.var_estado, foreground="#666666").pack(
            side="bottom", anchor="w", pady=(10, 0))

    def _grupo(self, padre, titulo, botones):
        marco = ttk.LabelFrame(padre, text=titulo, padding=10)
        marco.pack(fill="x", pady=6)
        for texto, comando in botones:
            ttk.Button(marco, text=texto, command=comando).pack(side="left", padx=(0, 8))

    # ------------------------------------------------------------------
    # Contactos
    # ------------------------------------------------------------------
    def _abrir_contactos(self, pestana):
        ventana = self._ventana_contactos
        if ventana is not None and ventana.winfo_exists():
            ventana.seleccionar_pestana(pestana)
            ventana.lift()
            ventana.focus_force()
        else:
            self._ventana_contactos = ContactosWindow(self, pestana_inicial=pestana)

    # ------------------------------------------------------------------
    # Exportar
    # ------------------------------------------------------------------
    def _exportar_json(self):
        try:
            ruta = exportar_json()
        except Exception as error:
            mostrar_error(error, "Exportar a JSON", parent=self)
            return
        messagebox.showinfo("Exportar a JSON", f"Contactos exportados correctamente a:\n{ruta}", parent=self)

    def _generar_pdf(self):
        # El PDF se genera a partir del JSON, por eso se exporta primero:
        # así el reporte siempre refleja el contenido actual del archivo.
        try:
            ruta_json = exportar_json()
            ruta_pdf = generar_pdf(ruta_json)
        except Exception as error:
            mostrar_error(error, "Generar reporte PDF", parent=self)
            return
        messagebox.showinfo(
            "Generar reporte PDF",
            f"Reporte generado correctamente.\n\nJSON: {ruta_json}\nPDF: {ruta_pdf}",
            parent=self,
        )

    # ------------------------------------------------------------------
    # Herramientas
    # ------------------------------------------------------------------
    def _actualizar_estado_integridad(self, correcta, mensaje):
        etiqueta = "correcta" if correcta else "ALERTA"
        self.var_estado.set(f"Integridad del archivo: {etiqueta} — {mensaje}")

    def _verificar_al_iniciar(self):
        """Verificación automática al abrir la aplicación (requisito del enunciado)."""
        try:
            correcta, mensaje = verificar_integridad()
        except Exception as error:
            self.var_estado.set("Integridad del archivo: no se pudo verificar")
            mostrar_error(error, "Verificación de integridad", parent=self)
            return

        self._actualizar_estado_integridad(correcta, mensaje)
        if not correcta:
            messagebox.showwarning(
                "Archivo modificado",
                f"{mensaje}\n\nEl archivo de contactos fue modificado fuera de la aplicación.",
                parent=self,
            )

    def _verificar_integridad(self):
        """Verificación manual desde Herramientas."""
        try:
            correcta, mensaje = verificar_integridad()
        except Exception as error:
            mostrar_error(error, "Verificar integridad", parent=self)
            return

        self._actualizar_estado_integridad(correcta, mensaje)
        if correcta:
            messagebox.showinfo("Verificar integridad", mensaje, parent=self)
        else:
            messagebox.showwarning("Verificar integridad", mensaje, parent=self)

    def _crear_respaldo(self):
        try:
            resultado = crear_respaldo()
        except Exception as error:
            mostrar_error(error, "Crear respaldo ZIP", parent=self)
            return

        original = resultado["tamano_original"]
        comprimido = resultado["tamano_comprimido"]
        reduccion = (1 - comprimido / original) * 100 if original else 0
        messagebox.showinfo(
            "Crear respaldo ZIP",
            f"Respaldo creado en:\n{resultado['ruta']}\n\n"
            f"Tamaño original: {original:,} bytes\n"
            f"Tamaño comprimido: {comprimido:,} bytes\n"
            f"Reducción: {reduccion:.1f}%",
            parent=self,
        )

    def _abrir_info(self):
        InfoWindow(self)

    # ------------------------------------------------------------------
    # Ayuda (simulada, como pide el enunciado)
    # ------------------------------------------------------------------
    def _ayuda_simulada(self):
        messagebox.showinfo("Ayuda", "Opción simulada: no tiene funcionalidad real.", parent=self)