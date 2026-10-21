import tkinter as tk
from tkinter import messagebox
import logging

from config.docker_manager import DockerManager
from database.db_connection import DatabaseConnection
from ui.styles.theme import Theme
from ui.views.login_view import LoginView

# Configurar logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def iniciar_aplicacion():
    # 1. Verificar Infraestructura (DevOps)
    logging.info("Verificando entorno de base de datos...")
    if not DockerManager.asegurar_base_datos():
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        messagebox.showerror("Error Crítico",
                             "No se pudo iniciar MySQL (ni local ni en Docker).\nVerifica tu instalación.")
        return

    # 2. Inicializar conexión (Singleton)
    try:
        DatabaseConnection()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo conectar a la base de datos:\n{e}")
        return

    # 3. Arrancar la UI
    root = tk.Tk()
    root.title("Biblioteca del Campus - Acceso")
    root.geometry("1000x700")  # Tamaño inicial
    root.configure(bg=Theme.COLOR_BG_LIGHT)

    # Aplicar nuestros estilos personalizados
    Theme.aplicar_estilos(root)

    # Cargar la vista de Login
    app = LoginView(root)

    root.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()