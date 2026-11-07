#Buscar y Modificar|

"""
contactos_window.py
-------------------
Ventana de contactos con tres pestañas: Agregar, Buscar por ID y Modificar.

Esta ventana NO toca archivos: solo recolecta lo que escribe el usuario, lo
valida de forma básica y se lo entrega a core.contactos_manager. Todo el
acceso aleatorio (seek/tell), el índice y el hash viven en core/.

Contrato con core (ver README):
    agregar_contacto(contacto)            -> {"registro": int, "posicion": int}
    buscar_por_id(id)                     -> (contacto, {"registro": int, "posicion": int})
    modificar_contacto(id, nuevos_datos)  -> {"registro": int, "posicion": int}
  - buscar_por_id y modificar_contacto lanzan KeyError si el id no existe.
  - agregar_contacto lanza ValueError si el id ya existe o hay un dato inválido.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from core.contactos_manager import agregar_contacto, buscar_por_id, modificar_contacto
from gui.mensajes import mostrar_error

# (clave del diccionario, etiqueta visible). El id se maneja aparte porque no es editable.
CAMPOS = [
    ("nombre", "Nombre"),
    ("telefono", "Teléfono"),
    ("correo", "Correo"),
    ("ciudad", "Ciudad"),
]


class ContactosWindow(tk.Toplevel):
    def __init__(self, master, pestana_inicial=0):
        super().__init__(master)
        self.title("Contactos")
        self.geometry("520x560")
        self.resizable(True, True)

        self._id_cargado = None  # id del contacto que se está editando en la pestaña Modificar

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_agregar = ttk.Frame(self.notebook, padding=20)
        self.tab_buscar = ttk.Frame(self.notebook, padding=20)
        self.tab_modificar = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_agregar, text="Agregar")
        self.notebook.add(self.tab_buscar, text="Buscar por ID")
        self.notebook.add(self.tab_modificar, text="Modificar")

        self._construir_agregar()
        self._construir_buscar()
        self._construir_modificar()

        self.seleccionar_pestana(pestana_inicial)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def seleccionar_pestana(self, indice):
        self.notebook.select(indice)

    def _campo(self, padre, etiqueta, ancho=40):
        """Crea una etiqueta + entrada y devuelve la entrada."""
        ttk.Label(padre, text=etiqueta).pack(anchor="w", pady=(8, 2))
        entrada = ttk.Entry(padre, width=ancho)
        entrada.pack(anchor="w")
        return entrada

    def _leer_id(self, texto):
        """Convierte el texto del campo ID a entero positivo o lanza ValueError."""
        try:
            valor = int(texto.strip())
        except ValueError:
            raise ValueError("El ID debe ser un número entero.")
        if valor <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        return valor

    def _leer_datos(self, campos):
        """Lee y limpia los campos de texto; el nombre es obligatorio."""
        datos = {clave: entrada.get().strip() for clave, entrada in campos.items()}
        if not datos["nombre"]:
            raise ValueError("El nombre es obligatorio.")
        return datos

    def _formatear_contacto(self, contacto, info):
        return (
            f"ID: {contacto.get('id', '')}\n"
            f"Nombre: {contacto.get('nombre', '')}\n"
            f"Teléfono: {contacto.get('telefono', '')}\n"
            f"Correo: {contacto.get('correo', '')}\n"
            f"Ciudad: {contacto.get('ciudad', '')}\n\n"
            f"Registro #{info.get('registro', '?')} del archivo\n"
            f"Posición en el archivo (tell): {info.get('posicion', '?')} bytes"
        )

    # ------------------------------------------------------------------
    # Pestaña: Agregar
    # ------------------------------------------------------------------
    def _construir_agregar(self):
        self.ag_id = self._campo(self.tab_agregar, "ID (número entero único)", 15)
        self.ag_campos = {clave: self._campo(self.tab_agregar, etiqueta) for clave, etiqueta in CAMPOS}
        ttk.Button(self.tab_agregar, text="Agregar contacto", style="Accent.TButton",
                   command=self._agregar).pack(anchor="w", pady=20)

    def _agregar(self):
        try:
            id_contacto = self._leer_id(self.ag_id.get())
            datos = self._leer_datos(self.ag_campos)
            info = agregar_contacto({"id": id_contacto, **datos})
        except Exception as error:
            mostrar_error(error, "Agregar contacto", parent=self)
            return

        messagebox.showinfo(
            "Agregar contacto",
            f"Contacto agregado correctamente.\n\n"
            f"Registro #{info.get('registro', '?')}\n"
            f"Posición en el archivo (tell): {info.get('posicion', '?')} bytes",
            parent=self,
        )
        self.ag_id.delete(0, "end")
        for entrada in self.ag_campos.values():
            entrada.delete(0, "end")

    # ------------------------------------------------------------------
    # Pestaña: Buscar por ID
    # ------------------------------------------------------------------
    def _construir_buscar(self):
        self.bu_id = self._campo(self.tab_buscar, "ID del contacto", 15)
        self.bu_id.bind("<Return>", lambda evento: self._buscar())
        ttk.Button(self.tab_buscar, text="Buscar", style="Accent.TButton",
                   command=self._buscar).pack(anchor="w", pady=15)
        self.var_resultado = tk.StringVar(value="")
        ttk.Label(self.tab_buscar, textvariable=self.var_resultado, justify="left").pack(anchor="w", pady=10)

    def _buscar(self):
        self.var_resultado.set("")
        try:
            id_contacto = self._leer_id(self.bu_id.get())
            contacto, info = buscar_por_id(id_contacto)
        except KeyError:
            messagebox.showwarning("Buscar contacto",
                                   f"No existe un contacto con el ID {self.bu_id.get().strip()}.",
                                   parent=self)
            return
        except Exception as error:
            mostrar_error(error, "Buscar contacto", parent=self)
            return

        self.var_resultado.set(self._formatear_contacto(contacto, info))

    # ------------------------------------------------------------------
    # Pestaña: Modificar
    # ------------------------------------------------------------------
    def _construir_modificar(self):
        self.mo_id = self._campo(self.tab_modificar, "ID del contacto a modificar", 15)
        self.mo_id.bind("<Return>", lambda evento: self._cargar_para_modificar())
        ttk.Button(self.tab_modificar, text="Cargar contacto",
                   command=self._cargar_para_modificar).pack(anchor="w", pady=10)

        self.var_mo_info = tk.StringVar(value="Carga un contacto para poder editarlo.")
        ttk.Label(self.tab_modificar, textvariable=self.var_mo_info).pack(anchor="w", pady=(0, 5))

        self.mo_campos = {clave: self._campo(self.tab_modificar, etiqueta) for clave, etiqueta in CAMPOS}
        self.btn_guardar_mod = ttk.Button(self.tab_modificar, text="Guardar cambios",
                                          style="Accent.TButton", command=self._guardar_modificacion)
        self.btn_guardar_mod.pack(anchor="w", pady=15)

        self._habilitar_edicion(False)

    def _habilitar_edicion(self, habilitar):
        estado = "normal" if habilitar else "disabled"
        for entrada in self.mo_campos.values():
            entrada.config(state=estado)
        self.btn_guardar_mod.config(state=estado)

    def _cargar_para_modificar(self):
        try:
            id_contacto = self._leer_id(self.mo_id.get())
            contacto, info = buscar_por_id(id_contacto)
        except KeyError:
            self._id_cargado = None
            self._habilitar_edicion(False)
            self.var_mo_info.set("Carga un contacto para poder editarlo.")
            messagebox.showwarning("Modificar contacto",
                                   f"No existe un contacto con el ID {self.mo_id.get().strip()}.",
                                   parent=self)
            return
        except Exception as error:
            mostrar_error(error, "Modificar contacto", parent=self)
            return

        self._id_cargado = id_contacto
        self._habilitar_edicion(True)  # primero habilitar: un campo deshabilitado no admite insert()
        for clave, entrada in self.mo_campos.items():
            entrada.delete(0, "end")
            entrada.insert(0, contacto.get(clave, ""))
        self.var_mo_info.set(
            f"Editando contacto ID {id_contacto} "
            f"(registro #{info.get('registro', '?')}, posición {info.get('posicion', '?')})"
        )

    def _guardar_modificacion(self):
        if self._id_cargado is None:
            messagebox.showwarning("Modificar contacto", "Primero carga un contacto.", parent=self)
            return
        try:
            datos = self._leer_datos(self.mo_campos)
            info = modificar_contacto(self._id_cargado, datos)
        except KeyError:
            messagebox.showwarning("Modificar contacto",
                                   f"El contacto con ID {self._id_cargado} ya no existe.",
                                   parent=self)
            return
        except Exception as error:
            mostrar_error(error, "Modificar contacto", parent=self)
            return

        messagebox.showinfo(
            "Modificar contacto",
            f"Contacto actualizado correctamente.\n\n"
            f"Registro #{info.get('registro', '?')} sobrescrito en la posición "
            f"{info.get('posicion', '?')} (tell).",
            parent=self,
        )