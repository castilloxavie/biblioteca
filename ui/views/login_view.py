import tkinter as tk
from tkinter import ttk, messagebox
from security.auth_manager import AuthManager
from security.mfa_totp import MFAManager
from security.audit_logger import AuditLogger
from database.db_connection import DatabaseConnection
from ui.styles.theme import Theme


class LoginView:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseConnection()
        self.usuario_autenticado = None

        for widget in self.root.winfo_children():
            widget.destroy()

        self.construir_ui()

    def construir_ui(self):
        # Contenedor principal centrado
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Tarjeta de Login (Card)
        card = ttk.Frame(main_frame, style="Card.TFrame", padding=40)
        card.pack()

        # Título
        ttk.Label(card, text="Biblioteca del Campus", style="Title.TLabel", background=Theme.COLOR_WHITE).pack(
            pady=(0, 5))
        ttk.Label(card, text="Ingresa tus credenciales para continuar", style="Subtitle.TLabel",
                  background=Theme.COLOR_WHITE).pack(pady=(0, 20))

        # Campo Usuario
        ttk.Label(card, text="Usuario:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_username = ttk.Entry(card, width=35)
        self.entry_username.pack(pady=(0, 15))

        # Campo Contraseña
        ttk.Label(card, text="Contraseña:", background=Theme.COLOR_WHITE).pack(anchor="w")
        self.entry_password = ttk.Entry(card, width=35, show="*")
        self.entry_password.pack(pady=(0, 25))

        # Botón Login

        # ... (código anterior del botón de login)
        btn_login = ttk.Button(card, text="Iniciar Sesión", style="Primary.TButton", command=self.procesar_login)
        btn_login.pack(fill="x", pady=(0, 10))

        # --- NUEVO BOTÓN DE REGISTRO ---
        btn_registro = tk.Button(card, text="¿No tienes cuenta? Regístrate aquí", bg=Theme.COLOR_WHITE,
                                 fg=Theme.COLOR_ACCENT, bd=0, cursor="hand2", command=self.ir_a_registro)
        btn_registro.pack()
        # -------------------------------

        # Agrega este método a la clase LoginView

    def ir_a_registro(self):
        from ui.views.register_view import RegisterView
        # Destruir vista actual y cargar Registro
        RegisterView(self.root)

    def procesar_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa usuario y contraseña.")
            return

        # 1. Buscar usuario en BD (Usando SP)
        resultado = self.db.ejecutar_sp("sp_obtener_usuario_login", (username,))

        if not resultado or len(resultado) == 0:
            AuditLogger.registrar_acceso_fallido(username, "Usuario no encontrado")
            messagebox.showerror("Error", "Credenciales incorrectas.")
            return

        usuario = resultado[0]  # El SP devuelve una lista de diccionarios

        if not usuario['activo']:
            AuditLogger.registrar_acceso_fallido(username, "Usuario inactivo")
            messagebox.showerror("Error", "Esta cuenta ha sido desactivada.")
            return

        # 2. Verificar contraseña con Bcrypt
        if not AuthManager.verificar_password(password, usuario['password_hash']):
            AuditLogger.registrar_acceso_fallido(username, "Contraseña incorrecta")
            messagebox.showerror("Error", "Credenciales incorrectas.")
            return

        # 3. Verificar MFA (Si está configurado)
        if usuario['mfa_secret']:
            if not self.solicitar_mfa(usuario['mfa_secret']):
                AuditLogger.registrar_acceso_fallido(username, "Fallo en código MFA")
                messagebox.showerror("Error", "Código MFA incorrecto.")
                return

        # 4. Login Exitoso
        self.usuario_autenticado = usuario
        AuditLogger.registrar(usuario['id'], "LOGIN_EXITOSO", f"Rol: {usuario['rol']}")

        messagebox.showinfo("Bienvenido", f"Bienvenido de nuevo, {usuario['username']}!")
        self.abrir_dashboard()

    def solicitar_mfa(self, secreto):
        """Ventana modal rápida para pedir el código de 6 dígitos"""
        mfa_win = tk.Toplevel(self.root)
        mfa_win.title("Autenticación de Doble Factor")
        mfa_win.geometry("350x200")
        mfa_win.configure(bg=Theme.COLOR_WHITE)
        mfa_win.grab_set()  # Bloquear ventana principal hasta que se cierre esta

        ttk.Label(mfa_win, text="Ingresa el código de 6 dígitos\nde tu aplicación autenticadora:",
                  background=Theme.COLOR_WHITE, justify="center").pack(pady=15)

        entry_codigo = ttk.Entry(mfa_win, width=15, justify="center")
        entry_codigo.pack()

        resultado = [False]  # Lista para guardar el estado

        def verificar():
            codigo = entry_codigo.get().strip()
            if MFAManager.verificar_codigo(secreto, codigo):
                resultado[0] = True
                mfa_win.destroy()
            else:
                messagebox.showerror("Error", "Código incorrecto o expirado.")
                entry_codigo.delete(0, tk.END)

        ttk.Button(mfa_win, text="Verificar", style="Primary.TButton", command=verificar).pack(pady=15)

        self.root.wait_window(mfa_win)  # Esperar a que se cierre la ventana modal
        return resultado[0]

    def abrir_dashboard(self):
        from ui.views.dashboard_view import DashboardView
        DashboardView(self.root, self.usuario_autenticado)