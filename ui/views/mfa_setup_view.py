import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import ImageTk, Image

from ui.styles.theme import Theme
from security.mfa_totp import MFAManager
from security.audit_logger import AuditLogger
from database.db_connection import DatabaseConnection


class MFASetupView:
    def __init__(self, parent, usuario):
        self.parent = parent
        self.usuario = usuario
        self.db = DatabaseConnection()

        # Generar un nuevo secreto temporal
        self.secreto_temporal = MFAManager.generar_secreto()

        self.win = tk.Toplevel(parent)
        self.win.title("Configurar Doble Factor (MFA)")
        self.win.geometry("450x550")
        self.win.configure(bg=Theme.COLOR_WHITE)
        self.win.grab_set()  # Bloquear ventana de fondo

        self.construir_ui()

    def construir_ui(self):
        tk.Label(self.win, text="Seguridad: Doble Factor", font=("Segoe UI", 16, "bold"),
                 bg=Theme.COLOR_WHITE, fg=Theme.COLOR_TEXT_DARK).pack(pady=(20, 10))

        tk.Label(self.win, text="1. Escanea este código con Google Authenticator\no Authy en tu teléfono:",
                 font=("Segoe UI", 10), bg=Theme.COLOR_WHITE, justify="center").pack(pady=10)

        # Generar QR
        uri = MFAManager.obtener_uri_qr(self.usuario['username'], self.secreto_temporal)
        qr = qrcode.make(uri)
        qr = qr.resize((200, 200), Image.Resampling.LANCZOS)
        self.img_qr = ImageTk.PhotoImage(qr)

        lbl_qr = tk.Label(self.win, image=self.img_qr, bg=Theme.COLOR_WHITE)
        lbl_qr.pack(pady=10)

        tk.Label(self.win, text="2. Ingresa el código de 6 dígitos que aparece:",
                 font=("Segoe UI", 10), bg=Theme.COLOR_WHITE).pack(pady=(10, 5))

        self.entry_codigo = ttk.Entry(self.win, width=15, justify="center", font=("Segoe UI", 14))
        self.entry_codigo.pack(pady=5)

        btn_verificar = ttk.Button(self.win, text="Verificar y Activar", style="Primary.TButton",
                                   command=self.verificar_y_guardar)
        btn_verificar.pack(pady=20, fill="x", padx=50)

    def verificar_y_guardar(self):
        codigo = self.entry_codigo.get().strip()

        if not codigo:
            messagebox.showwarning("Atención", "Por favor ingresa el código.")
            return

        # Validar el código con el secreto temporal
        if MFAManager.verificar_codigo(self.secreto_temporal, codigo):
            # El código es correcto, guardamos en BD
            resultado = self.db.ejecutar_sp("sp_actualizar_mfa_secret", (self.usuario['id'], self.secreto_temporal))

            if resultado is not False:
                messagebox.showinfo("Éxito",
                                    "MFA activado correctamente.\nLa próxima vez que inicies sesión se te pedirá este código.")
                AuditLogger.registrar(self.usuario['id'], "MFA_ACTIVADO",
                                      "El usuario activó la autenticación de doble factor")

                # Actualizar el diccionario local del usuario para que la sesión actual lo sepa
                self.usuario['mfa_secret'] = self.secreto_temporal
                self.win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar el secreto en la base de datos.")
        else:
            messagebox.showerror("Error", "Código incorrecto o expirado. Intenta de nuevo.")
            self.entry_codigo.delete(0, tk.END)