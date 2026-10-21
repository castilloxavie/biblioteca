import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class ActiveLoansView:
    def __init__(self, parent_frame, usuario, ir_a_nuevo_prestamo):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.ir_a_nuevo_prestamo = ir_a_nuevo_prestamo

        self.construir_ui()
        self.cargar_prestamos()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)

        tk.Label(header, text="Préstamos Activos", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(side="left")

        ttk.Button(header, text="+ Nuevo Préstamo", style="Primary.TButton",
                   command=self.ir_a_nuevo_prestamo).pack(side="right")

        # Contenedor con Scroll para las tarjetas
        self.canvas = tk.Canvas(self.parent, bg=Theme.COLOR_BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Theme.COLOR_BG_LIGHT)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))

    def cargar_prestamos(self):
        # Limpiar tarjetas anteriores
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Primero, actualizamos los vencidos en la BD (Job de mantenimiento)
        self.db.ejecutar_sp("sp_actualizar_prestamos_vencidos")

        # Traer préstamos
        prestamos = self.db.ejecutar_sp("sp_obtener_prestamos_activos")

        if not prestamos:
            tk.Label(self.scrollable_frame, text="No hay préstamos activos en este momento.",
                     font=("Segoe UI", 12), bg=Theme.COLOR_BG_LIGHT, fg="#7f8c8d").pack(pady=30)
            return

        # Crear una cuadrícula para las tarjetas (3 columnas)
        row, col = 0, 0
        for p in prestamos:
            self.crear_tarjeta_prestamo(p, row, col)
            col += 1
            if col > 2:  # 3 tarjetas por fila
                col = 0
                row += 1

    def crear_tarjeta_prestamo(self, prestamo, row, col):
        # Determinar estado y color
        dias_retraso = prestamo['dias_retraso']
        es_vencido = dias_retraso > 0

        color_borde = "#c0392b" if es_vencido else "#27ae60"  # Rojo vs Verde

        # Tarjeta
        card = tk.Frame(self.scrollable_frame, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0",
                        highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Línea superior de color
        tk.Frame(card, bg=color_borde, height=4).pack(fill="x")

        # Contenido
        content = tk.Frame(card, bg=Theme.COLOR_WHITE)
        content.pack(padx=15, pady=15, fill="both", expand=True)

        tk.Label(content, text=prestamo['titulo'], font=("Segoe UI", 12, "bold"),
                 bg=Theme.COLOR_WHITE, wraplength=200, justify="left").pack(anchor="w")

        tk.Label(content, text=f"{prestamo['nombre_lector']} • Estudiante/Docente",
                 font=("Segoe UI", 9), bg=Theme.COLOR_WHITE, fg="#7f8c8d").pack(anchor="w", pady=(2, 10))

        tk.Label(content, text=f"{prestamo['fecha_prestamo']} → {prestamo['fecha_vencimiento']}",
                 font=("Segoe UI", 9), bg=Theme.COLOR_WHITE).pack(anchor="w")

        # Texto de estado
        if es_vencido:
            texto_estado = f"Vencido hace {dias_retraso} días"
            color_estado = "#c0392b"
        else:
            dias_restantes = abs(dias_retraso)
            texto_estado = f"Faltan {dias_restantes} días"
            color_estado = "#27ae60"

        tk.Label(content, text=texto_estado, font=("Segoe UI", 9, "bold"),
                 bg=Theme.COLOR_WHITE, fg=color_estado).pack(anchor="w", pady=(5, 15))

        # Botón de Devolución
        btn_devolver = ttk.Button(content, text="Registrar devolución",
                                  command=lambda pid=prestamo['id']: self.registrar_devolucion(pid))
        btn_devolver.pack(anchor="w", fill="x")

        # Asegurar que las columnas se expandan uniformemente
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)

    def registrar_devolucion(self, prestamo_id):
        confirm = messagebox.askyesno("Confirmar", "¿El lector ha devuelto el libro físicamente?")
        if confirm:
            resultado = self.db.ejecutar_sp("sp_registrar_devolucion", (prestamo_id,))
            if resultado is False:
                messagebox.showerror("Error", "No se pudo registrar la devolución.")
            else:
                messagebox.showinfo("Éxito", "Devolución registrada. El stock ha sido actualizado.")
                AuditLogger.registrar(self.usuario['id'], "REGISTRAR_DEVOLUCION", f"Préstamo ID: {prestamo_id}")
                self.cargar_prestamos()  # Refrescar la vista