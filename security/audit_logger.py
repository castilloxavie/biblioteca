import socket
import logging
from database.db_connection import DatabaseConnection


class AuditLogger:
    @staticmethod
    def registrar(usuario_id, accion: str, detalles: str = ""):
        try:
            db = DatabaseConnection()
            ip_local = socket.gethostbyname(socket.gethostname())

            # BLINDAJE DE FK: Si el ID es 0, None o vacío, lo forzamos a None (NULL en BD)
            id_seguro = usuario_id if usuario_id and usuario_id > 0 else None

            db.ejecutar_sp(
                "sp_registrar_auditoria",
                (id_seguro, accion, detalles, ip_local)
            )
        except Exception as e:
            logging.error(f"Fallo crítico en auditoría: {e}")

    @staticmethod
    def registrar_acceso_fallido(username: str, razon: str):
        try:
            db = DatabaseConnection()
            ip_local = socket.gethostbyname(socket.gethostname())
            detalles = f"Usuario: {username} | Razón: {razon}"

            db.ejecutar_sp(
                "sp_registrar_auditoria",
                (None, "LOGIN_FALLIDO", detalles, ip_local)
            )
        except Exception as e:
            logging.error(f"Fallo al registrar acceso fallido: {e}")