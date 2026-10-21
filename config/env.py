import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "4825")
    DB_NAME = os.getenv("DB_NAME", "biblioteca_db")

    # configuracion de Docker
    DOCKER_CONTAINER_NAME = "biblioteca_mysql"
    DOCKER_IMAGE = "mysql:8.0"