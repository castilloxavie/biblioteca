import os


class Config:
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "tu_usuario_aqui")

    # NUNCA pongas tu contraseña real aquí
    DB_PASSWORD = os.getenv("DB_PASSWORD", "TU_CONTRASEÑA_AQUI")

    DB_NAME = os.getenv("DB_NAME", "biblioteca_db")

    # Configuración de Docker
    DOCKER_CONTAINER_NAME = "biblioteca_mysql"
    DOCKER_IMAGE = "mysql:8.0"
