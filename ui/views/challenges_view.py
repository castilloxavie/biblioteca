import tkinter as tk
from tkinter import ttk
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection


class ChallengesView:
    def __init__(self, parent_frame, usuario):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()

        # Lista de retos (Hardcodeados según tu imagen)
        self.retos = [
            (1, "Agrega el campo 'Editorial' al formulario de libros y muéstralo en la tabla.", "Básico"),
            (2, "Cambia la paleta de colores del sitio modificando solo las variables de :root.", "Básico"),
            (3, "Agrega un botón 'Editar' en la tabla que cargue los datos del libro en el formulario.", "Intermedio"),
            (4, "Valida que el correo del préstamo termine en @universidad.edu.co usando setCustomValidity.",
             "Intermedio"),
            (5, "Impide que un mismo lector tenga más de 3 préstamos activos.", "Intermedio"),
            (6, "Crea una nueva opción de menú 'Lectores' con su propio formulario y listado.", "Avanzado"),
            (7, "Muestra en la tarjeta de un préstamo vencido la multa calculada automáticamente.", "Avanzado"),
            (8, "Agrega un botón para exportar el catálogo a un archivo CSV.", "Avanzado")
        ]

        self.checkboxes_vars = {}
        self.construir_ui()
        self.cargar_progreso()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)
        tk.Label(header, text="Retos para el Estudiante", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        # Card principal
        card = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        content = tk.Frame(card, bg=Theme.COLOR_WHITE)
        content.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(content, text="Amplía este proyecto", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_WHITE).pack(anchor="w")
        tk.Label(content, text="Marca cada reto a medida que lo completes; tu avance se guarda automáticamente.",
                 font=("Segoe UI", 10), bg=Theme.COLOR_WHITE, fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

        # Lista de retos
        for r_id, texto, nivel in self.retos:
            frame = tk.Frame(content, bg=Theme.COLOR_WHITE)
            frame.pack(fill="x", pady=5)

            var = tk.BooleanVar()
            self.checkboxes_vars[r_id] = var

            # Checkbox
            chk = ttk.Checkbutton(frame, variable=var, command=lambda i=r_id: self.toggle_reto(i))
            chk.pack(side="left")

            # Texto del reto
            tk.Label(frame, text=f"{r_id}. {texto}", bg=Theme.COLOR_WHITE,
                     font=("Segoe UI", 10), justify="left").pack(side="left", padx=5)

            # Etiqueta de nivel
            color_nivel = "#3498db" if nivel == "Básico" else ("#f39c12" if nivel == "Intermedio" else "#e74c3c")
            lbl_nivel = tk.Label(frame, text=nivel, bg=Theme.COLOR_WHITE, fg=color_nivel,
                                 font=("Segoe UI", 8, "bold"), borderwidth=1, relief="solid", padx=5)
            lbl_nivel.pack(side="left", padx=10)

        # Barra de progreso
        progress_frame = tk.Frame(content, bg=Theme.COLOR_WHITE)
        progress_frame.pack(fill="x", pady=(30, 10))

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.lbl_porcentaje = tk.Label(progress_frame, text="0 %", bg=Theme.COLOR_WHITE,
                                       font=("Segoe UI", 12, "bold"), fg=Theme.COLOR_TEXT_DARK)
        self.lbl_porcentaje.pack(side="right")

    def cargar_progreso(self):
        # Consultar la BD
        datos = self.db.ejecutar_sp("sp_obtener_progreso_retos", (self.usuario['id'],))

        completados = 0
        if datos:
            for fila in datos:
                reto_id = fila['reto_id']
                if reto_id in self.checkboxes_vars:
                    self.checkboxes_vars[reto_id].set(bool(fila['completado']))
                    if fila['completado']:
                        completados += 1

        self.actualizar_barra(completados)

    def toggle_reto(self, reto_id):
        esta_completado = self.checkboxes_vars[reto_id].get()

        # Guardar en BD
        self.db.ejecutar_sp("sp_actualizar_reto", (self.usuario['id'], reto_id, esta_completado))

        # Recalcular progreso
        completados = sum(1 for var in self.checkboxes_vars.values() if var.get())
        self.actualizar_barra(completados)

    def actualizar_barra(self, completados):
        total = len(self.retos)
        porcentaje = int((completados / total) * 100)

        self.progress_bar['value'] = porcentaje
        self.lbl_porcentaje.config(text=f"{porcentaje} %")