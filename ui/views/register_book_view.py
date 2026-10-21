import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class RegisterBookView:
    def __init__(self, parent_frame, usuario, volver_catalogo):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.volver_catalogo = volver_catalogo  # Callback para volver a la tabla

        self.construir_ui()

    def construir_ui(self):
        # Limpiar el frame principal
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)

        tk.Label(header, text="Registrar Nuevo Libro", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")
        tk.Label(header, text="Los campos marcados con * son obligatorios.",
                 font=("Segoe UI", 10), bg=Theme.COLOR_BG_LIGHT, fg="#7f8c8d").pack(anchor="w", pady=(5, 0))

        # Formulario (Card)
        form_frame = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        grid = tk.Frame(form_frame, bg=Theme.COLOR_WHITE)
        grid.pack(padx=30, pady=30, fill="both", expand=True)

        # Fila 1: Título y Autor
        tk.Label(grid, text="Título *", bg=Theme.COLOR_WHITE).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_titulo = ttk.Entry(grid, width=40)
        self.entry_titulo.grid(row=1, column=0, padx=(0, 20), pady=(0, 15), sticky="ew")

        tk.Label(grid, text="Autor *", bg=Theme.COLOR_WHITE).grid(row=0, column=1, sticky="w", pady=5)
        self.entry_autor = ttk.Entry(grid, width=40)
        self.entry_autor.grid(row=1, column=1, pady=(0, 15), sticky="ew")

        # Fila 2: ISBN, Año, Ejemplares
        tk.Label(grid, text="ISBN (13 dígitos) *", bg=Theme.COLOR_WHITE).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_isbn = ttk.Entry(grid, width=40)
        self.entry_isbn.grid(row=3, column=0, padx=(0, 20), pady=(0, 15), sticky="ew")

        frame_mitad = tk.Frame(grid, bg=Theme.COLOR_WHITE)
        frame_mitad.grid(row=3, column=1, sticky="ew")

        tk.Label(grid, text="Año Publicación *", bg=Theme.COLOR_WHITE).grid(row=2, column=1, sticky="w", pady=5)
        self.entry_anio = ttk.Entry(frame_mitad, width=15)
        self.entry_anio.pack(side="left", padx=(0, 20))

        tk.Label(frame_mitad, text="Ejemplares *", bg=Theme.COLOR_WHITE).pack(side="left")
        self.entry_ejemplares = ttk.Entry(frame_mitad, width=10)
        self.entry_ejemplares.pack(side="left")

        # Fila 3: Categoría y Formato
        tk.Label(grid, text="Categoría *", bg=Theme.COLOR_WHITE).grid(row=4, column=0, sticky="w", pady=5)
        self.combo_categoria = ttk.Combobox(grid, state="readonly", width=37)
        self.combo_categoria.grid(row=5, column=0, padx=(0, 20), pady=(0, 15), sticky="ew")
        self.cargar_categorias()

        tk.Label(grid, text="Formato *", bg=Theme.COLOR_WHITE).grid(row=4, column=1, sticky="w", pady=5)
        self.formato_var = tk.StringVar(value="Físico")
        frame_formato = tk.Frame(grid, bg=Theme.COLOR_WHITE)
        frame_formato.grid(row=5, column=1, sticky="w", pady=(0, 15))
        ttk.Radiobutton(frame_formato, text="Físico", variable=self.formato_var, value="Físico").pack(side="left",
                                                                                                      padx=(0, 15))
        ttk.Radiobutton(frame_formato, text="Digital", variable=self.formato_var, value="Digital").pack(side="left")

        # Fila 4: Etiquetas y Sinopsis
        tk.Label(grid, text="Etiquetas (Opcional)", bg=Theme.COLOR_WHITE).grid(row=6, column=0, sticky="w", pady=5)
        self.entry_etiquetas = ttk.Entry(grid, width=40)
        self.entry_etiquetas.grid(row=7, column=0, padx=(0, 20), pady=(0, 15), sticky="ew")

        tk.Label(grid, text="Sinopsis (Opcional)", bg=Theme.COLOR_WHITE).grid(row=6, column=1, sticky="w", pady=5)
        self.text_sinopsis = tk.Text(grid, height=4, width=40, font=("Segoe UI", 9))
        self.text_sinopsis.grid(row=7, column=1, pady=(0, 15), sticky="ew")

        # Botones
        btn_frame = tk.Frame(form_frame, bg=Theme.COLOR_WHITE)
        btn_frame.pack(fill="x", padx=30, pady=(0, 30))

        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side="right", padx=10)
        ttk.Button(btn_frame, text="Guardar Libro", style="Primary.TButton", command=self.guardar_libro).pack(
            side="right")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def cargar_categorias(self):
        datos = self.db.ejecutar_sp("sp_obtener_categorias")
        if datos:
            self.categorias = {fila['nombre']: fila['id'] for fila in datos}
            self.combo_categoria['values'] = list(self.categorias.keys())
            if self.combo_categoria['values']:
                self.combo_categoria.current(0)

    def limpiar_formulario(self):
        self.entry_titulo.delete(0, tk.END)
        self.entry_autor.delete(0, tk.END)
        self.entry_isbn.delete(0, tk.END)
        self.entry_anio.delete(0, tk.END)
        self.entry_ejemplares.delete(0, tk.END)
        self.entry_etiquetas.delete(0, tk.END)
        self.text_sinopsis.delete("1.0", tk.END)

    def guardar_libro(self):
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        isbn = self.entry_isbn.get().strip()
        anio = self.entry_anio.get().strip()
        ejemplares = self.entry_ejemplares.get().strip()
        categoria_nombre = self.combo_categoria.get()
        formato = self.formato_var.get()
        etiquetas = self.entry_etiquetas.get().strip()
        sinopsis = self.text_sinopsis.get("1.0", tk.END).strip()

        # Validaciones
        if not titulo or not autor or not isbn or not anio or not ejemplares:
            messagebox.showwarning("Atención", "Los campos con * son obligatorios.")
            return
        if len(isbn) != 13 or not isbn.isdigit():
            messagebox.showerror("Error", "El ISBN debe tener exactamente 13 dígitos numéricos.")
            return
        if not anio.isdigit() or int(anio) < 1000 or int(anio) > 2100:
            messagebox.showerror("Error", "Ingresa un año de publicación válido.")
            return
        if not ejemplares.isdigit() or int(ejemplares) <= 0:
            messagebox.showerror("Error", "El número de ejemplares debe ser mayor a 0.")
            return

        categoria_id = self.categorias.get(categoria_nombre)

        # Llamada al SP
        resultado = self.db.ejecutar_sp("sp_crear_libro",
                                        (titulo, autor, isbn, int(anio), int(ejemplares),
                                         categoria_id, formato, sinopsis, etiquetas))

        if resultado is False:
            messagebox.showerror("Error", "No se pudo guardar. ¿El ISBN ya existe?")
        else:
            messagebox.showinfo("Éxito", "Libro registrado correctamente.")
            AuditLogger.registrar(self.usuario['id'], "CREAR_LIBRO", f"Libro: {titulo} (ISBN: {isbn})")
            self.limpiar_formulario()
            # Opcional: Volver al catálogo después de guardar
            self.volver_catalogo()