CREATE DATABASE IF NOT EXISTS biblioteca_db
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE biblioteca_db;

CREATE TABLE usuarios(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol ENUM('ADMIN', 'BIBLIOTECARIO', 'ESTUDIANTE') DEFAULT 'ESTUDIANTE',
    mfa_secret VARCHAR(32) DEFAULT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    anio_publicacion YEAR,
    ejemplares_totales INT NOT NULL,
    ejemplares_disponibles INT NOT NULL,
    categoria_id INT,
    formato ENUM('Físico', 'Digital') DEFAULT 'Físico',
    sinopsis TEXT,
    etiquetas VARCHAR(255),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
);

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libro_id INT NOT NULL,
    usuario_id INT NOT NULL,
    nombre_lector VARCHAR(100) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    fecha_devolucion DATE DEFAULT NULL,
    estado ENUM('Activo', 'Devuelto', 'Vencido') DEFAULT 'Activo',
    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

CREATE TABLE multas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT UNIQUE NOT NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    dias_retraso INT NOT NULL,
    pagada BOOLEAN DEFAULT FALSE,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prestamo_id) REFERENCES prestamos(id) ON DELETE CASCADE
);

CREATE TABLE auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT DEFAULT NULL,
    accion VARCHAR(100) NOT NULL,
    detalles TEXT,
    ip_origen VARCHAR(45),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE TABLE encuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    calificacion TINYINT NOT NULL,
    servicios_usados VARCHAR(255),
    probabilidad_recomendar TINYINT,
    comentarios TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE TABLE configuracion_ui (
    usuario_id INT PRIMARY KEY,
    color_acento VARCHAR(7) DEFAULT '#C8960C',
    tamano_fuente INT DEFAULT 14,
    modo_oscuro BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);