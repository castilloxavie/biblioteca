import tkinter as tk
from tkinter import ttk, messagebox
from security.auth_manager import AuthManager
from security.audit_logger import AuditLogger
from database.db_connection import DatabaseConnection
from ui.styles.theme import Theme


class RegisterView:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseConnection()

        # Limpiar la ventana actual antes de dibujar el registro
        for widget in self.root.winfo_children():
            widget.destroy()

        self.construir_ui()

    def construir_ui(self):
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=40)
        card.pack()

        ttk.Label(card, text="Crear Cuenta", style="Title.TLabel", background=Theme.COLOR_WHITE).pack(pady=(0, 5))
        ttk.Label(card, text="Regístrate para acceder a la biblioteca", style="Subtitle.TLabel",
                  background=Theme.COLOR_WHITE).pack(pady=(0, 20))

        # Campo Usuario
        ttk.Label(card, text="Nombre de Usuario:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_username = ttk.Entry(card, width=35)
        self.entry_username.pack(pady=(0, 10))

        # Campo Email
        ttk.Label(card, text="Correo Institucional:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_email = ttk.Entry(card, width=35)
        self.entry_email.pack(pady=(0, 10))

        # Campo Contraseña
        ttk.Label(card, text="Contraseña:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_password = ttk.Entry(card, width=35, show="*")
        self.entry_password.pack(pady=(0, 10))

        # Confirmar Contraseña
        ttk.Label(card, text="Confirmar Contraseña:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_confirm = ttk.Entry(card, width=35, show="*")
        self.entry_confirm.pack(pady=(0, 20))

        # Botón Registrar
        ttk.Button(card, text="Registrarse", style="Primary.TButton", command=self.procesar_registro).pack(fill="x",
                                                                                                           pady=(0, 10))

        # Botón Volver al Login (Estilo simple)
        btn_volver = tk.Button(card, text="¿Ya tienes cuenta? Inicia sesión", bg=Theme.COLOR_WHITE,
                               fg=Theme.COLOR_ACCENT, bd=0, cursor="hand2", command=self.volver_al_login)
        btn_volver.pack()

    def procesar_registro(self):
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()

        # 1. Validaciones básicas
        if not username or not email or not password:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        if len(password) < 6:
            messagebox.showwarning("Seguridad", "La contraseña debe tener al menos 6 caracteres.")
            return

        # 2. Hashear la contraseña (Bcrypt)
        try:
            hash_seguro = AuthManager.generar_hash(password)
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo encriptar la contraseña: {e}")
            return

        # 3. Guardar en BD usando el SP
        # Por defecto, los nuevos registros serán 'ESTUDIANTE' según nuestra arquitectura
        resultado = self.db.ejecutar_sp("sp_registrar_usuario", (username, hash_seguro, email, "ESTUDIANTE"))

        # 4. Verificar respuesta
        if resultado is False:  # Nuestro db_connection devuelve False si el SP lanza excepción (ej. duplicado)
            messagebox.showerror("Error", "El nombre de usuario o el correo ya están registrados.")
            AuditLogger.registrar_acceso_fallido(username, "Intento de registro con datos duplicados")
        else:
            # Registro exitoso
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Ahora puedes iniciar sesión.")

            # --- CORRECCIÓN AQUÍ ---
            # Cambiamos el 0 por None para evitar el error de Llave Foránea (1452) en MySQL
            AuditLogger.registrar(None, "REGISTRO_USUARIO", f"Nuevo usuario: {username} ({email})")
            # -----------------------

            self.volver_al_login()

    def volver_al_login(self):
        from ui.views.login_view import LoginView
        # Destruir vista actual y cargar Login
        LoginView(self.root)