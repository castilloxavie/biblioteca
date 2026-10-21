import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles.theme import Theme
from database.db_connection import DatabaseConnection
from security.audit_logger import AuditLogger
from security.auth_manager import AuthManager
from ui.views.catalog_view import CatalogView
from ui.views.register_book_view import RegisterBookView
from ui.views.new_loan_view import NewLoanView
from ui.views.active_loans_view import ActiveLoansView
from ui.views.fines_calculator_view import FinesCalculatorView
from ui.views.survey_view import SurveyView
from ui.views.challenges_view import ChallengesView
from ui.views.customization_view import CustomizationView



class DashboardView:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.db = DatabaseConnection()

        # Limpiar la ventana de Login
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("1200x750")
        self.root.title("Biblioteca del Campus - Panel Principal")

        # Registrar en auditoría que el usuario entró al dashboard
        AuditLogger.registrar(self.usuario['id'], "ACCESO_DASHBOARD", "Usuario visualizando el panel principal")

        # Cargar preferencias guardadas en la BD
        datos_ui = self.db.ejecutar_sp("sp_obtener_config_ui", (self.usuario['id'],))
        if datos_ui and datos_ui[0]['modo_oscuro'] is not None:
            Theme.set_dark_mode(bool(datos_ui[0]['modo_oscuro']))
            Theme.aplicar_estilos(self.root)

        self.construir_sidebar()
        self.construir_area_principal()

    def refrescar_tema(self):
        # 1. Aplicar estilos globales
        Theme.aplicar_estilos(self.root)
        # 2. Destruir todo y volver a dibujar el Dashboard
        for widget in self.root.winfo_children():
            widget.destroy()
        self.construir_sidebar()
        self.construir_area_principal()
        # 3. Volver a cargar la vista de personalización
        self.mostrar_customization()

    def mostrar_customization(self):
        CustomizationView(self.main_content, self.usuario, self.refrescar_tema)

    def actualizar_sidebar(self):
        # Destruye y vuelve a dibujar el menú con el nuevo color
        self.sidebar.destroy()
        self.construir_sidebar()

    def construir_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=Theme.COLOR_PRIMARY_DARK, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Título
        tk.Label(self.sidebar, text="Biblioteca", font=("Segoe UI", 18, "bold"),
                 bg=Theme.COLOR_PRIMARY_DARK, fg=Theme.COLOR_WHITE).pack(pady=(30, 5), padx=20, anchor="w")
        tk.Label(self.sidebar, text="del Campus", font=("Segoe UI", 10),
                 bg=Theme.COLOR_PRIMARY_DARK, fg="#bdc3c7").pack(pady=(0, 30), padx=20, anchor="w")

        # Botones del Menú Básico
        self.crear_boton_menu("🏠 Inicio", self.mostrar_inicio, activo=True)
        self.crear_boton_menu("📚 Catálogo", self.mostrar_catalogo)
        self.crear_boton_menu("🔄 Préstamos", self.mostrar_prestamos)

        # --- BOTÓN EXCLUSIVO PARA ADMINISTRADORES (Paso 7.5) ---
        if self.usuario['rol'] == 'ADMIN':
            self.crear_boton_menu("👥 Usuarios", self.mostrar_usuarios)
        # -------------------------------------------------------

        self.crear_boton_menu("🛠️ Herramientas", self.mostrar_herramientas)
        self.crear_boton_menu("🔐 Configurar MFA", self.abrir_config_mfa)
        self.crear_boton_menu("⭐ Encuesta de servicio", self.mostrar_encuesta)
        self.crear_boton_menu("🎨 Personalizar Apariencia", self.mostrar_customization)
        self.crear_boton_menu("🏆 Retos para el Estudiante", self.mostrar_retos)

        # Espacio flexible
        tk.Frame(self.sidebar, bg=Theme.COLOR_PRIMARY_DARK).pack(fill="y", expand=True)

        # Info del Usuario
        tk.Label(self.sidebar, text=f"👤 {self.usuario['username']}\n({self.usuario['rol']})",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.COLOR_PRIMARY_DARK, fg=Theme.COLOR_ACCENT, justify="left").pack(pady=(10, 5), padx=20,
                                                                                          anchor="w")

        # Botón Cerrar Sesión
        btn_logout = tk.Button(self.sidebar, text="Cerrar Sesión", bg="#c0392b", fg="white",
                               bd=0, cursor="hand2", command=self.cerrar_sesion)
        btn_logout.pack(pady=10, padx=20, fill="x")

    def crear_boton_menu(self, texto, comando, activo=False):
        bg_color = Theme.COLOR_ACCENT if activo else Theme.COLOR_PRIMARY_DARK
        fg_color = Theme.COLOR_WHITE if activo else "#ecf0f1"

        btn = tk.Button(self.sidebar, text=texto, bg=bg_color, fg=fg_color,
                        font=("Segoe UI", 11), bd=0, anchor="w", padx=20, pady=10,
                        cursor="hand2", command=comando, activebackground=Theme.COLOR_ACCENT)
        btn.pack(fill="x", pady=2)

    def construir_area_principal(self):
        self.main_content = tk.Frame(self.root, bg=Theme.COLOR_BG_LIGHT)
        self.main_content.pack(side="right", fill="both", expand=True)
        self.mostrar_inicio()

    def limpiar_area_principal(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_area_principal()

        header_frame = tk.Frame(self.main_content, bg=Theme.COLOR_BG_LIGHT)
        header_frame.pack(fill="x", padx=30, pady=20)

        tk.Label(header_frame, text="Inicio", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w")

        tk.Label(header_frame, text=f"Buenas tardes, {self.usuario['username']}",
                 font=("Segoe UI", 22, "bold"), bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(pady=(10, 5),
                                                                                                        anchor="w")
        tk.Label(header_frame, text="Este panel resume el estado del catálogo y de los préstamos.",
                 font=("Segoe UI", 11), bg=Theme.COLOR_BG_LIGHT, fg="#7f8c8d").pack(pady=(0, 20), anchor="w")

        self.stats_frame = tk.Frame(self.main_content, bg=Theme.COLOR_BG_LIGHT)
        self.stats_frame.pack(fill="x", padx=30)
        self.actualizar_tarjetas()

        activity_frame = tk.Frame(self.main_content, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0",
                                  highlightthickness=1)
        activity_frame.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(activity_frame, text="Actividad reciente", font=("Segoe UI", 14, "bold"),
                 bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w", padx=20, pady=(20, 10))

        tk.Label(activity_frame, text="Aún no hay actividad. Registra un libro o un préstamo para verla aquí.",
                 font=("Segoe UI", 10), bg=Theme.COLOR_WHITE, fg="#7f8c8d").pack(anchor="w", padx=20)

        btn_restaurar = tk.Button(activity_frame, text="Restaurar datos de ejemplo",
                                  bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK,
                                  font=("Segoe UI", 10, "bold"), relief="solid", bd=1,
                                  cursor="hand2", command=self.restaurar_datos)
        btn_restaurar.pack(anchor="w", padx=20, pady=20)

    def actualizar_tarjetas(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        datos = self.db.ejecutar_sp("sp_obtener_estadisticas")
        if datos and len(datos) > 0:
            stats = datos[0]
            self.crear_tarjeta(self.stats_frame, "Títulos en catálogo", stats['total_titulos'], "#2c3e50")
            self.crear_tarjeta(self.stats_frame, "Ejemplares disponibles", stats['ejemplares_disponibles'], "#27ae60")
            self.crear_tarjeta(self.stats_frame, "Préstamos activos", stats['prestamos_activos'], "#d35400")
            self.crear_tarjeta(self.stats_frame, "Préstamos vencidos", stats['prestamos_vencidos'], "#c0392b")

    def crear_tarjeta(self, parent, titulo, valor, color_borde):
        card = tk.Frame(parent, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Frame(card, bg=color_borde, height=5).pack(fill="x")
        tk.Label(card, text=str(valor), font=("Segoe UI", 28, "bold"),
                 bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(card, text=titulo, font=("Segoe UI", 10),
                 bg=Theme.COLOR_WHITE, fg="#7f8c8d").pack(anchor="w", padx=15, pady=(0, 15))

    def restaurar_datos(self):
        resultado = self.db.ejecutar_sp("sp_restaurar_datos_ejemplo")
        if resultado is not False:
            messagebox.showinfo("Éxito", "Datos de ejemplo restaurados correctamente.")
            AuditLogger.registrar(self.usuario['id'], "RESTAURAR_DATOS", "Se restauraron datos de prueba en el sistema")
            self.actualizar_tarjetas()
        else:
            messagebox.showerror("Error", "No se pudieron restaurar los datos. Verifica la consola.")

    # =================================================================
    # NUEVO MÓDULO: GESTIÓN DE USUARIOS (Solo para ADMIN)
    # =================================================================
    def mostrar_usuarios(self):
        self.limpiar_area_principal()

        tk.Label(self.main_content, text="Gestión de Usuarios", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_BG_LIGHT, fg=Theme.COLOR_TEXT_DARK).pack(pady=20, padx=30, anchor="w")

        tk.Label(self.main_content, text="Crea nuevas cuentas y asigna roles en el sistema.",
                 font=("Segoe UI", 11), bg=Theme.COLOR_BG_LIGHT, fg="#7f8c8d").pack(pady=(0, 20), padx=30, anchor="w")

        # Formulario de Creación
        form_frame = tk.Frame(self.main_content, bg=Theme.COLOR_WHITE, highlightbackground="#e0e0e0",
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=30, pady=10)

        grid_frame = tk.Frame(form_frame, bg=Theme.COLOR_WHITE)
        grid_frame.pack(padx=20, pady=20)

        tk.Label(grid_frame, text="Usuario:", bg=Theme.COLOR_WHITE).grid(row=0, column=0, sticky="w", pady=5)
        entry_user = ttk.Entry(grid_frame, width=30)
        entry_user.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(grid_frame, text="Email:", bg=Theme.COLOR_WHITE).grid(row=1, column=0, sticky="w", pady=5)
        entry_email = ttk.Entry(grid_frame, width=30)
        entry_email.grid(row=1, column=1, pady=5, padx=10)

        tk.Label(grid_frame, text="Contraseña:", bg=Theme.COLOR_WHITE).grid(row=2, column=0, sticky="w", pady=5)
        entry_pass = ttk.Entry(grid_frame, width=30, show="*")
        entry_pass.grid(row=2, column=1, pady=5, padx=10)

        tk.Label(grid_frame, text="Rol:", bg=Theme.COLOR_WHITE).grid(row=3, column=0, sticky="w", pady=5)
        combo_rol = ttk.Combobox(grid_frame, values=["ESTUDIANTE", "BIBLIOTECARIO", "ADMIN"], state="readonly",
                                 width=27)
        combo_rol.current(0)  # Por defecto Estudiante
        combo_rol.grid(row=3, column=1, pady=5, padx=10)

        def guardar_usuario():
            user = entry_user.get().strip()
            email = entry_email.get().strip()
            pwd = entry_pass.get()
            rol = combo_rol.get()

            if not user or not email or not pwd:
                messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
                return

            hash_seguro = AuthManager.generar_hash(pwd)

            # Ejecutamos el SP de registro
            resultado = self.db.ejecutar_sp("sp_registrar_usuario", (user, hash_seguro, email, rol))

            if resultado is False:
                messagebox.showerror("Error", "El usuario o correo ya existen.")
            else:
                messagebox.showinfo("Éxito", f"Usuario {user} creado con rol {rol}.")
                # AUDITORÍA: Amarramos esta acción al ID del ADMIN que la ejecutó
                AuditLogger.registrar(self.usuario['id'], "CREAR_USUARIO_ADMIN",
                                      f"Creó al usuario {user} con rol {rol}")
                # Limpiar campos
                entry_user.delete(0, tk.END)
                entry_email.delete(0, tk.END)
                entry_pass.delete(0, tk.END)
                self.cargar_tabla_usuarios(tabla_frame)  # Refrescar tabla

        btn_guardar = ttk.Button(form_frame, text="Crear Usuario", style="Primary.TButton", command=guardar_usuario)
        btn_guardar.pack(pady=(0, 20))

        # Tabla de Usuarios Existentes
        tabla_frame = tk.Frame(self.main_content, bg=Theme.COLOR_BG_LIGHT)
        tabla_frame.pack(fill="both", expand=True, padx=30, pady=10)
        self.cargar_tabla_usuarios(tabla_frame)

    def cargar_tabla_usuarios(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        columnas = ("ID", "Usuario", "Email", "Rol", "Estado")
        tree = ttk.Treeview(parent, columns=columnas, show="headings", height=8)

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col != "ID" else 50, anchor="center")

        datos = self.db.ejecutar_sp("sp_obtener_usuarios")
        if datos:
            for fila in datos:
                estado = "Activo" if fila['activo'] else "Inactivo"
                tree.insert("", "end", values=(fila['id'], fila['username'], fila['email'], fila['rol'], estado))

        tree.pack(fill="both", expand=True)

    # =================================================================

    def mostrar_registrar_libro(self):
        RegisterBookView(self.main_content, self.usuario, self.mostrar_catalogo)

    def mostrar_catalogo(self):
        CatalogView(self.main_content, self.usuario, self.mostrar_registrar_libro, self.mostrar_nuevo_prestamo)

    def mostrar_prestamos(self):
        ActiveLoansView(self.main_content, self.usuario, self.mostrar_nuevo_prestamo)

    def mostrar_nuevo_prestamo(self, titulo_libro=None):
        NewLoanView(self.main_content, self.usuario, self.mostrar_prestamos, titulo_libro)

    def mostrar_herramientas(self):
        self.limpiar_area_principal()
        FinesCalculatorView(self.main_content, self.usuario)

    def mostrar_encuesta(self):
        SurveyView(self.main_content, self.usuario)

    def cerrar_sesion(self):
        AuditLogger.registrar(self.usuario['id'], "CIERRE_SESION", "El usuario cerró sesión")
        from ui.views.login_view import LoginView
        self.root.geometry("1000x700")
        LoginView(self.root)

    def abrir_config_mfa(self):
        from ui.views.mfa_setup_view import MFASetupView
        MFASetupView(self.root, self.usuario)

    def mostrar_customization(self):
        CustomizationView(self.main_content, self.usuario, self.actualizar_sidebar)

    def mostrar_retos(self):
        ChallengesView(self.main_content, self.usuario)