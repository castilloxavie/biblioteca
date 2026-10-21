import docker
import time
import logging
from config.env import Config


class DockerManager:
    @staticmethod
    def asegurar_base_datos():
        """
        Verifica si hay conexión a MySQL local. Si no, intenta levantar Docker.
        """
        try:
            # 1. Intentar conectar a un MySQL local (si el usuario ya lo tiene)
            import mysql.connector
            mysql.connector.connect(
                host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD
            ).close()
            logging.info("MySQL local detectado. Omitiendo Docker.")
            return True
        except Exception:
            logging.warning("MySQL local no detectado. Iniciando protocolo Docker...")

        # 2. Si falla, usar Docker
        try:
            client = docker.from_env()

            # Verificar si el contenedor ya existe
            try:
                contenedor = client.containers.get(Config.DOCKER_CONTAINER_NAME)
                if contenedor.status != 'running':
                    contenedor.start()
                    time.sleep(10)  # Esperar a que MySQL arranque
                logging.info("Contenedor MySQL de Docker en ejecución.")
                return True
            except docker.errors.NotFound:
                # Si no existe, lo creamos
                logging.info("Creando contenedor MySQL por primera vez...")
                client.containers.run(
                    Config.DOCKER_IMAGE,
                    name=Config.DOCKER_CONTAINER_NAME,
                    environment={"MYSQL_ROOT_PASSWORD": Config.DB_PASSWORD},
                    ports={'3306/tcp': Config.DB_PORT},
                    detach=True,
                    remove=False
                )
                time.sleep(15)  # Esperar a que inicialice
                return True

        except docker.errors.DockerException as e:
            logging.error(f"Docker no está instalado o no está corriendo: {e}")
            return False