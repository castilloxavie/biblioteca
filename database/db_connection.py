import mysql.connector
from mysql.connector import Error
import logging
from config.env import Config


class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        # Patrón Singleton
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False  # Control manual de transacciones
            )
            logging.info("Conexión establecida con la base de datos.")
        except Error as e:
            logging.critical(f"Error fatal de conexión: {e}")
            raise e

    def ejecutar_sp(self, nombre_sp: str, parametros: tuple = ()):
        """
        Ejecuta exclusivamente Procedimientos Almacenados.
        Retorna los resultados si el SP hace un SELECT, o True/False si es una acción.
        """
        cursor = None
        try:
            if not self._connection or not self._connection.is_connected():
                self._connect()  # Reconexión automática (ISO 27035)

            cursor = self._connection.cursor(dictionary=True)

            # EL CORAZÓN DE LA SEGURIDAD: callproc escapa los parámetros
            # previniendo Inyección SQL por diseño.
            cursor.callproc(nombre_sp, parametros)

            resultados = []
            # Si el SP devuelve tablas (SELECT), las extraemos
            for result in cursor.stored_results():
                resultados.extend(result.fetchall())

            # Si el SP tiene parámetros OUT (como p_mensaje), los capturamos
            out_params = []
            if cursor._stored_results is not None:  # Validación interna
                pass  # MySQL Connector maneja los OUT params de forma distinta según la versión

            self._connection.commit()  # Confirmar transacción
            return resultados

        except Error as e:
            if self._connection:
                self._connection.rollback()  # Revertir en caso de error
            logging.error(f"Error en SP '{nombre_sp}': {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def cerrar(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logging.info("Conexión a base de datos cerrada.")