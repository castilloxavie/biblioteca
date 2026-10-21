import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class NewLoanView:
    def __init__(self, parent_frame, usuario, volver_a_prestamos, libro_preseleccionado=None):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.volver_a_prestamos = volver_a_prestamos
        self.libro_preseleccionado = libro_preseleccionado

        self.construir_ui()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)

        tk.Label(header, text="Registrar Préstamo", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        form_frame = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        grid = tk.Frame(form_frame, bg=Theme.COLOR_WHITE)
        grid.pack(padx=30, pady=30, fill="both", expand=True)

        # Libro (Combobox con los disponibles)
        tk.Label(grid, text="Libro *", bg=Theme.COLOR_WHITE).grid(row=0, column=0, sticky="w", pady=5)
        self.combo_libros = ttk.Combobox(grid, state="readonly", width=50)
        self.combo_libros.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        self.cargar_libros_disponibles()

        # Nombre del Lector
        tk.Label(grid, text="Nombre del lector *", bg=Theme.COLOR_WHITE).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_lector = ttk.Entry(grid, width=40)
        self.entry_lector.grid(row=3, column=0, padx=(0, 20), pady=(0, 15), sticky="ew")

        # Correo Institucional
        tk.Label(grid, text="Correo institucional *", bg=Theme.COLOR_WHITE).grid(row=2, column=1, sticky="w", pady=5)
        self.entry_email = ttk.Entry(grid, width=40)
        self.entry_email.grid(row=3, column=1, pady=(0, 15), sticky="ew")

        # Tipo de Usuario
        tk.Label(grid, text="Tipo de usuario *", bg=Theme.COLOR_WHITE).grid(row=4, column=0, sticky="w", pady=5)
        self.tipo_usuario_var = tk.StringVar(value="Estudiante")
        frame_tipo = tk.Frame(grid, bg=Theme.COLOR_WHITE)
        frame_tipo.grid(row=5, column=0, sticky="w", pady=(0, 15))

        # Al cambiar el radio button, actualizamos la fecha
        ttk.Radiobutton(frame_tipo, text="Estudiante (8 días)", variable=self.tipo_usuario_var,
                        value="Estudiante", command=self.actualizar_fecha).pack(side="left", padx=(0, 15))
        ttk.Radiobutton(frame_tipo, text="Docente (15 días)", variable=self.tipo_usuario_var,
                        value="Docente", command=self.actualizar_fecha).pack(side="left")

        # Fechas
        tk.Label(grid, text="Fecha de préstamo *", bg=Theme.COLOR_WHITE).grid(row=6, column=0, sticky="w", pady=5)
        self.entry_fecha_prestamo = ttk.Entry(grid, width=20)
        self.entry_fecha_prestamo.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_prestamo.config(state="readonly")  # Solo lectura para evitar errores
        self.entry_fecha_prestamo.grid(row=7, column=0, padx=(0, 20), pady=(0, 15), sticky="w")

        tk.Label(grid, text="Fecha de devolución (Calculada)", bg=Theme.COLOR_WHITE).grid(row=6, column=1, sticky="w",
                                                                                          pady=5)
        self.entry_fecha_devolucion = ttk.Entry(grid, width=20)
        self.entry_fecha_devolucion.config(state="readonly")
        self.entry_fecha_devolucion.grid(row=7, column=1, pady=(0, 15), sticky="w")

        self.actualizar_fecha()  # Llamada inicial para calcular la primera fecha

        # Botón Guardar
        btn_guardar = ttk.Button(form_frame, text="Registrar Préstamo", style="Primary.TButton",
                                 command=self.guardar_prestamo)
        btn_guardar.pack(pady=(0, 30), padx=30, anchor="e")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def cargar_libros_disponibles(self):
        # Solo traemos libros con stock > 0
        resultados = self.db.ejecutar_sp("sp_buscar_libros", ("", None, True))
        self.libros_dict = {}

        if resultados:
            valores = []
            for libro in resultados:
                # Formato visual: Título (Stock: X)
                texto = f"{libro['titulo']} (Stock: {libro['ejemplares_disponibles']})"
                valores.append(texto)
                self.libros_dict[texto] = libro['id']

            self.combo_libros['values'] = valores
            if valores:
                self.combo_libros.current(0)

                if self.libro_preseleccionado:
                    for i, val in enumerate(valores):
                        if self.libro_preseleccionado in val:
                            self.combo_libros.current(i)
                            break

        else:
            self.combo_libros['values'] = ["No hay libros disponibles"]
            self.combo_libros.current(0)

    def actualizar_fecha(self):
        tipo = self.tipo_usuario_var.get()
        dias = 8 if tipo == "Estudiante" else 15
        fecha_dev = datetime.now() + timedelta(days=dias)

        self.entry_fecha_devolucion.config(state="normal")
        self.entry_fecha_devolucion.delete(0, tk.END)
        self.entry_fecha_devolucion.insert(0, fecha_dev.strftime("%Y-%m-%d"))
        self.entry_fecha_devolucion.config(state="readonly")

    def guardar_prestamo(self):
        libro_sel = self.combo_libros.get()
        lector = self.entry_lector.get().strip()
        email = self.entry_email.get().strip()

        # Validaciones
        if not libro_sel or libro_sel == "No hay libros disponibles":
            messagebox.showwarning("Atención", "Debes seleccionar un libro válido.")
            return
        if not lector or not email:
            messagebox.showwarning("Atención", "El nombre y correo del lector son obligatorios.")
            return
        if not email.endswith("@universidad.edu.co"):
            messagebox.showerror("Error", "El correo debe pertenecer al dominio @universidad.edu.co")
            return

        libro_id = self.libros_dict.get(libro_sel)
        fecha_prestamo = self.entry_fecha_prestamo.get()
        fecha_devolucion = self.entry_fecha_devolucion.get()

        # Llamada al SP. Nota: sp_crear_prestamo usa un parámetro OUT (p_mensaje)
        # El conector de MySQL a veces no maneja bien los OUT en callproc directo,
        # así que el SP devuelve el mensaje de error si falla.

        try:
            resultado = self.db.ejecutar_sp("sp_crear_prestamo",
                                            (libro_id, self.usuario['id'], lector, fecha_prestamo, fecha_devolucion,
                                             ""))

            # Como nuestro db_connection no lee fácilmente los OUT params,
            # comprobamos si el SP falló revisando si el stock bajó o si hubo error.
            if resultado is False:
                messagebox.showerror("Error", "No se pudo registrar el préstamo. Verifica el stock.")
            else:
                messagebox.showinfo("Éxito", "Préstamo registrado exitosamente.")
                AuditLogger.registrar(self.usuario['id'], "CREAR_PRESTAMO", f"Libro ID: {libro_id} a {lector}")
                self.volver_a_prestamos()  # Recargar la vista de préstamos

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Fallo en la transacción: {e}")