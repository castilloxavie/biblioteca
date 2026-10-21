import bcrypt
import logging

class AuthManager:
    @staticmethod
    def generar_hash(password_plana: str) -> str:
        """
        Convierte una contraseña en un hash seguro con un 'salt' aleatorio.
        """
        try:
            # Convertimos a bytes (requerido por bcrypt)
            password_bytes = password_plana.encode('utf-8')

            # Generamos el salt y el hash (factor de coste 12)
            salt = bcrypt.gensalt(rounds=12)
            hash_bytes = bcrypt.hashpw(password_bytes, salt)
            return hash_bytes.decode('utf-8')
        except Exception as e:
            logging.error(f"Error al generar hash: {e}")
            raise e

    @staticmethod
    def verificar_password(password_plana: str, hash_guardado: str) -> bool:
        """
        Compara la contraseña ingresada con el hash de la base de datos.
        """
        try:
            return bcrypt.checkpw(
                password_plana.encode('utf-8'), 
                hash_guardado.encode('utf-8')
            )
        except Exception as e:
            logging.error(f"Error al verificar contraseña: {e}")
            return False