import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger


class CatalogView:
    def __init__(self, parent_frame, usuario, ir_a_registro, ir_a_prestamo):
        self.parent = parent_frame
        self.usuario = usuario
        self.db = DatabaseConnection()
        self.ir_a_registro = ir_a_registro
        self.ir_a_prestamo = ir_a_prestamo

        self.construir_ui()
        self.cargar_datos()

    def construir_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Encabezado
        header = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        header.pack(fill="x", padx=30, pady=20)

        tk.Label(header, text="Consultar Catálogo", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(side="left")

        ttk.Button(header, text="+ Registrar Libro", style="Primary.TButton",
                   command=self.ir_a_registro).pack(side="right")

        # Barra de Filtros (Card)
        filter_frame = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        filter_frame.pack(fill="x", padx=30, pady=(0, 15))

        inner_filter = tk.Frame(filter_frame, bg=Theme.COLOR_WHITE)
        inner_filter.pack(padx=20, pady=15, fill="x")

        tk.Label(inner_filter, text="Buscar:", bg=Theme.COLOR_WHITE).pack(side="left")
        self.entry_buscar = ttk.Entry(inner_filter, width=30)
        self.entry_buscar.pack(side="left", padx=(5, 20))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos())

        tk.Label(inner_filter, text="Categoría:", bg=Theme.COLOR_WHITE).pack(side="left")
        self.combo_filtro_cat = ttk.Combobox(inner_filter, state="readonly", width=20)
        self.combo_filtro_cat.pack(side="left", padx=(5, 20))
        self.combo_filtro_cat.bind("<<ComboboxSelected>>", lambda e: self.cargar_datos())

        self.var_solo_disponibles = tk.BooleanVar()
        ttk.Checkbutton(inner_filter, text="Solo con ejemplares", variable=self.var_solo_disponibles,
                        command=self.cargar_datos).pack(side="left", padx=20)

        self.cargar_filtros_categorias()

        # Tabla (Treeview)
        table_frame = tk.Frame(self.parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        columnas = ("ID", "Título", "Autor", "Año", "Categoría", "Stock", "Acciones")
        self.tree = ttk.Treeview(table_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Autor", text="Autor")
        self.tree.heading("Año", text="Año")
        self.tree.heading("Categoría", text="Categoría")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Acciones", text="Acciones")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Título", width=200, anchor="w")
        self.tree.column("Autor", width=150, anchor="w")
        self.tree.column("Año", width=60, anchor="center")
        self.tree.column("Categoría", width=100, anchor="center")
        self.tree.column("Stock", width=60, anchor="center")
        self.tree.column("Acciones", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Panel de Acciones (Botones debajo de la tabla)
        action_frame = tk.Frame(self.parent, bg=Theme.COLOR_BG_LIGHT)
        action_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.btn_prestar = ttk.Button(action_frame, text="Prestar", state="disabled", command=self.accion_prestar)
        self.btn_prestar.pack(side="left", padx=(0, 10))

        self.btn_eliminar = ttk.Button(action_frame, text="Eliminar", state="disabled", command=self.accion_eliminar)
        self.btn_eliminar.pack(side="left")

        # Evento de selección en la tabla
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def cargar_filtros_categorias(self):
        datos = self.db.ejecutar_sp("sp_obtener_categorias")
        if datos:
            self.categorias = {fila['nombre']: fila['id'] for fila in datos}
            valores = ["Todas las categorías"] + list(self.categorias.keys())
            self.combo_filtro_cat['values'] = valores
            self.combo_filtro_cat.current(0)

    def cargar_datos(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        termino = self.entry_buscar.get().strip()
        cat_sel = self.combo_filtro_cat.get()
        solo_disponibles = self.var_solo_disponibles.get()

        cat_id = None
        if cat_sel != "Todas las categorías" and cat_sel in self.categorias:
            cat_id = self.categorias[cat_sel]

        # Llamar al SP de búsqueda
        resultados = self.db.ejecutar_sp("sp_buscar_libros", (termino, cat_id, solo_disponibles))

        print(
            f"DEBUG CATALOGO: Enviando -> Termino: '{termino}', Cat_ID: {cat_id}, Solo_Disponibles: {solo_disponibles}")
        print(f"DEBUG CATALOGO: MySQL devolvió -> {resultados}")
        # ------------------------------------

        if resultados:
            for fila in resultados:
                stock = f"{fila['ejemplares_disponibles']}/{fila['ejemplares_totales']}"
                self.tree.insert("", "end", values=(
                    fila['id'], fila['titulo'], fila['autor'], fila['anio_publicacion'],
                    fila['categoria'] or "Sin categoría", stock, "Seleccionar..."
                ))

    def on_item_select(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            self.btn_prestar.config(state="normal")
            self.btn_eliminar.config(state="normal")
        else:
            self.btn_prestar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")

    def obtener_libro_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return None
        item = self.tree.item(seleccion[0])
        return item['values']  # [ID, Título, Autor, Año, Cat, Stock, Acc]

    def accion_eliminar(self):
        libro = self.obtener_libro_seleccionado()
        if not libro: return

        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el libro '{libro[1]}'?")
        if confirm:
            resultado = self.db.ejecutar_sp("sp_eliminar_libro", (libro[0],))
            # Nota: Nuestro SP devuelve un mensaje de error si tiene préstamos activos
            if resultado is False:
                messagebox.showerror("Error", "No se puede eliminar. Tiene préstamos activos o hubo un fallo.")
            else:
                messagebox.showinfo("Éxito", "Libro eliminado.")
                AuditLogger.registrar(self.usuario['id'], "ELIMINAR_LIBRO", f"Libro ID: {libro[0]} - {libro[1]}")
                self.cargar_datos()
                self.btn_prestar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")

    def accion_prestar(self):
        libro = self.obtener_libro_seleccionado()
        if not libro: return

        # Llamamos a la función de préstamos pasando el título del libro
        self.ir_a_prestamo(libro[1])