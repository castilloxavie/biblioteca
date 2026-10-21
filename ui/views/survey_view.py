import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class SurveyView:
    def __init__(self, parent_frame, usuario):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.rating = 0

        self.construir_ui()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)
        tk.Label(header, text="Encuesta de Servicio", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        # Card
        card = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        content = tk.Frame(card, bg=Theme.COLOR_WHITE)
        content.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(content, text="¿Cómo fue tu visita?", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_WHITE).pack(anchor="w", pady=(0, 20))

        # Estrellas
        tk.Label(content, text="Calificación general *", bg=Theme.COLOR_WHITE).pack(anchor="w")
        self.stars_frame = tk.Frame(content, bg=Theme.COLOR_WHITE)
        self.stars_frame.pack(anchor="w", pady=(0, 20))

        self.star_buttons = []
        for i in range(5):
            btn = tk.Button(self.stars_frame, text="☆", font=("Segoe UI", 24), bg=Theme.COLOR_WHITE, fg="#f1c40f", bd=0,
                            cursor="hand2",
                            command=lambda x=i + 1: self.set_rating(x))
            btn.pack(side="left")
            self.star_buttons.append(btn)

        # Servicios usados
        tk.Label(content, text="¿Qué servicios usaste?", bg=Theme.COLOR_WHITE).pack(anchor="w")
        services_frame = tk.Frame(content, bg=Theme.COLOR_WHITE)
        services_frame.pack(anchor="w", pady=(5, 20))

        self.service_vars = {}
        servicios = ["Préstamo", "Salas de estudio", "Computadores", "Bases de datos"]
        for s in servicios:
            var = tk.BooleanVar()
            self.service_vars[s] = var
            ttk.Checkbutton(services_frame, text=s, variable=var).pack(side="left", padx=(0, 15))

        # Probabilidad de recomendación
        tk.Label(content, text="¿Qué tan probable es que nos recomiendes? (1 al 10)", bg=Theme.COLOR_WHITE).pack(
            anchor="w")
        self.scale_rec = tk.Scale(content, from_=1, to=10, orient="horizontal", bg=Theme.COLOR_WHITE,
                                  highlightthickness=0)
        self.scale_rec.set(5)
        self.scale_rec.pack(fill="x", pady=(0, 20))

        # Comentarios
        tk.Label(content, text="Comentarios", bg=Theme.COLOR_WHITE).pack(anchor="w")
        self.text_comentarios = tk.Text(content, height=4, font=("Segoe UI", 10))
        self.text_comentarios.pack(fill="x", pady=(5, 20))

        # Botón Enviar
        ttk.Button(content, text="Enviar encuesta", style="Primary.TButton", command=self.guardar_encuesta).pack(
            anchor="e")

    def set_rating(self, rating):
        self.rating = rating
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.config(text="★")  # Estrella llena
            else:
                btn.config(text="☆")  # Estrella vacía

    def guardar_encuesta(self):
        if self.rating == 0:
            messagebox.showwarning("Atención", "Por favor, selecciona una calificación con las estrellas.")
            return

        servicios_usados = ", ".join([s for s, var in self.service_vars.items() if var.get()])
        probabilidad = self.scale_rec.get()
        comentarios = self.text_comentarios.get("1.0", tk.END).strip()

        # Llamar al SP
        resultado = self.db.ejecutar_sp("sp_guardar_encuesta",
                                        (self.usuario['id'], self.rating, servicios_usados, probabilidad, comentarios))

        if resultado is not False:
            messagebox.showinfo("Éxito", "¡Gracias por tu opinión! La encuesta ha sido guardada.")
            AuditLogger.registrar(self.usuario['id'], "ENCUESTA_COMPLETADA", f"Calificación: {self.rating}")
            # Limpiar formulario
            self.set_rating(0)
            for var in self.service_vars.values():
                var.set(False)
            self.scale_rec.set(5)
            self.text_comentarios.delete("1.0", tk.END)
        else:
            messagebox.showerror("Error", "No se pudo guardar la encuesta.")