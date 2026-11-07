"""
main.py
-------
Punto de entrada de la aplicación. Solo crea la ventana principal y
arranca el bucle de eventos; toda la lógica de archivos vive en core/
y la interfaz en gui/.

Ejecutar siempre desde la raíz del proyecto:
    python3 main.py
"""

from gui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()