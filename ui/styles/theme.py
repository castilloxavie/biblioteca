import tkinter as tk
from tkinter import ttk


class Theme:
    # Paleta Base
    COLOR_ACCENT = "#c69814"  # Dorado/Mostaza
    COLOR_PRIMARY_DARK = "#1e3228"  # Verde bosque
    COLOR_TEXT_LIGHT = "#ffffff"
    COLOR_DANGER = "#e74c3c"
    COLOR_SUCCESS = "#2ecc71"

    # Variables dinámicas (se sobrescriben según el modo)
    COLOR_BG_LIGHT = "#f4f6f5"
    COLOR_WHITE = "#ffffff"
    COLOR_TEXT_DARK = "#2c3e50"
    COLOR_BORDER = "#e0e0e0"

    # Estado global
    IS_DARK_MODE = False

    @classmethod
    def set_dark_mode(cls, is_dark):
        cls.IS_DARK_MODE = is_dark
        if is_dark:
            # Paleta Oscura Elegante
            cls.COLOR_BG_LIGHT = "#121212"  # Fondo principal oscuro
            cls.COLOR_WHITE = "#1e1e1e"  # Tarjetas/Cards oscuras
            cls.COLOR_TEXT_DARK = "#f4f6f5"  # Texto claro sobre fondo oscuro
            cls.COLOR_BORDER = "#333333"  # Bordes sutiles
            cls.COLOR_PRIMARY_DARK = "#0a0a0a"  # Sidebar casi negro
        else:
            # Paleta Clara Original
            cls.COLOR_BG_LIGHT = "#f4f6f5"
            cls.COLOR_WHITE = "#ffffff"
            cls.COLOR_TEXT_DARK = "#2c3e50"
            cls.COLOR_BORDER = "#e0e0e0"
            cls.COLOR_PRIMARY_DARK = "#1e3228"

    @classmethod
    def aplicar_estilos(cls, root):
        style = ttk.Style(root)
        style.theme_use('clam')

        # Estilos Dinámicos
        style.configure("Main.TFrame", background=cls.COLOR_BG_LIGHT)
        style.configure("Card.TFrame", background=cls.COLOR_WHITE, relief="solid", borderwidth=1)

        style.configure("Title.TLabel", background=cls.COLOR_BG_LIGHT, foreground=cls.COLOR_TEXT_DARK,
                        font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", background=cls.COLOR_BG_LIGHT, foreground="#7f8c8d", font=("Segoe UI", 11))

        style.configure("Primary.TButton",
                        font=("Segoe UI", 11, "bold"),
                        background=cls.COLOR_ACCENT,
                        foreground="#ffffff",
                        borderwidth=0,
                        focuscolor=cls.COLOR_ACCENT)
        style.map("Primary.TButton", background=[("active", "#a67c10")])

        style.configure("TEntry", padding=5, fieldbackground=cls.COLOR_WHITE, foreground=cls.COLOR_TEXT_DARK,
                        borderwidth=1)

        # Estilos para el Treeview (Tablas) para que se vean bien en oscuro
        style.configure("Treeview",
                        background=cls.COLOR_WHITE,
                        foreground=cls.COLOR_TEXT_DARK,
                        fieldbackground=cls.COLOR_WHITE,
                        rowheight=25)
        style.configure("Treeview.Heading",
                        background=cls.COLOR_BG_LIGHT,
                        foreground=cls.COLOR_TEXT_DARK,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", cls.COLOR_ACCENT)], foreground=[("selected", "#ffffff")])