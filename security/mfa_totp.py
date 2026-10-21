import pyotp

class MFAManager:
    @staticmethod
    def generar_secreto() -> str:
        """Genera una clave base32 única para el usuario."""
        return pyotp.random_base32()

    @staticmethod
    def obtener_uri_qr(username: str, secreto: str) -> str:
        """
        Genera la URI estándar (otpauth://) para que la UI de Tkinter
        pueda convertirla en una imagen de código QR.
        """
        return pyotp.totp.TOTP(secreto).provisioning_uri(
            name=username,
            issuer_name="Biblioteca del Campus"
        )

    @staticmethod
    def verificar_codigo(secreto: str, codigo_ingresado: str) -> bool:
        """
        Verifica si el código de 6 dígitos es válido (ventana de 30s).
        """
        totp = pyotp.TOTP(secreto)
        # valid_window=1 permite un margen de 30 segundos antes/después
        # por desfase de relojes, sin comprometer la seguridad.
        return totp.verify(codigo_ingresado, valid_window=1)