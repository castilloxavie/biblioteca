import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class CustomizationView:
    def __init__(self, parent_frame, usuario, callback_refresh_tema):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.callback_refresh_tema = callback_refresh_tema

        self.color_actual = Theme.COLOR_ACCENT
        self.construir_ui()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)
        tk.Label(header, text="Personalizar Apariencia", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        card = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground=Theme.COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        content = tk.Frame(card, bg=Theme.COLOR_WHITE)
        content.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(content, text="Cambia el estilo del sitio", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="Los cambios se aplican en tiempo real.",
                 font=("Segoe UI", 10), bg=Theme.COLOR_WHITE, fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

        row1 = tk.Frame(content, bg=Theme.COLOR_WHITE)
        row1.pack(fill="x", pady=(0, 20))

        # Color
        col1 = tk.Frame(row1, bg=Theme.COLOR_WHITE)
        col1.pack(side="left", expand=True, fill="x")
        tk.Label(col1, text="Color de acento", bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")
        self.btn_color = tk.Button(col1, bg=self.color_actual, width=10, height=1,
                                   command=self.elegir_color, relief="solid", bd=1)
        self.btn_color.pack(anchor="w", pady=5)

        # Tamaño fuente
        col2 = tk.Frame(row1, bg=Theme.COLOR_WHITE)
        col2.pack(side="left", expand=True, fill="x")
        tk.Label(col2, text="Tamaño de letra: 16px", bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")
        self.scale_font = tk.Scale(col2, from_=12, to=20, orient="horizontal", bg=Theme.COLOR_WHITE,
                                   fg=Theme.COLOR_TEXT_DARK, highlightthickness=0)
        self.scale_font.set(16)
        self.scale_font.pack(fill="x")

        # Modo Oscuro (AHORA ACTIVO)
        self.var_dark = tk.BooleanVar(value=Theme.IS_DARK_MODE)
        chk = ttk.Checkbutton(content, text="Activar Modo Oscuro", variable=self.var_dark,
                              command=self.toggle_modo_oscuro)
        chk.pack(anchor="w", pady=(0, 20))

        # Vista previa
        preview = tk.Frame(content, bg=Theme.COLOR_BG_LIGHT, highlightbackground=Theme.COLOR_BORDER,
                           highlightthickness=1)
        preview.pack(fill="x", pady=10)

        tk.Label(preview, text="Vista previa", font=("Segoe UI", 12, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w", padx=20, pady=(10, 5))
        tk.Label(preview, text="Así se ven los botones con tu configuración.",
                 font=("Segoe UI", 9), bg=Theme.COLOR_BG_LIGHT, fg="#7f8c8d").pack(anchor="w", padx=20, pady=(0, 10))

        self.btn_preview = tk.Button(preview, text="Botón principal", bg=self.color_actual, fg="white", padx=15, pady=5,
                                     bd=0)
        self.btn_preview.pack(anchor="w", padx=20, pady=(0, 20))

        ttk.Button(content, text="Guardar Cambios", style="Primary.TButton", command=self.guardar_config).pack(
            anchor="e")

    def elegir_color(self):
        color = colorchooser.askcolor(title="Selecciona un color", color=self.color_actual)[1]
        if color:
            self.color_actual = color
            self.btn_color.config(bg=color)
            Theme.COLOR_ACCENT = color
            Theme.aplicar_estilos(self.parent.winfo_toplevel())
            self.btn_preview.config(bg=color)

    def toggle_modo_oscuro(self):
        # Cambia el estado del tema y llama al Dashboard para que se redibuje
        Theme.set_dark_mode(self.var_dark.get())
        self.callback_refresh_tema()

    def guardar_config(self):
        fuente = self.scale_font.get()
        modo_oscuro = self.var_dark.get()

        self.db.ejecutar_sp("sp_guardar_config_ui", (self.usuario['id'], self.color_actual, fuente, modo_oscuro))
        messagebox.showinfo("Éxito", "Configuración guardada.\nSe mantendrá la próxima vez que inicies sesión.")
        AuditLogger.registrar(self.usuario['id'], "ACTUALIZAR_UI", f"Color: {self.color_actual}, Oscuro: {modo_oscuro}")