USE biblioteca_db;

-- =====================================================================
-- PASO PREVIO: AGREGAR COLUMNA PARA BORRADO LÓGICO
-- =====================================================================
-- Si la columna ya existe, MySQL ignorará este comando con un error (puedes ignorarlo).
ALTER TABLE libros ADD COLUMN activo BOOLEAN DEFAULT TRUE;

-- =====================================================================
-- LIMPIEZA TOTAL DE PROCEDIMIENTOS ALMACENADOS (Para evitar conflictos)
-- =====================================================================
DROP PROCEDURE IF EXISTS sp_registrar_usuario;
DROP PROCEDURE IF EXISTS sp_obtener_usuario_login;
DROP PROCEDURE IF EXISTS sp_actualizar_mfa_secret;
DROP PROCEDURE IF EXISTS sp_registrar_auditoria;
DROP PROCEDURE IF EXISTS sp_obtener_usuarios;

DROP PROCEDURE IF EXISTS sp_crear_libro;
DROP PROCEDURE IF EXISTS sp_obtener_libros;
DROP PROCEDURE IF EXISTS sp_buscar_libros;
DROP PROCEDURE IF EXISTS sp_actualizar_libro;
DROP PROCEDURE IF EXISTS sp_eliminar_libro;
DROP PROCEDURE IF EXISTS sp_obtener_categorias;

DROP PROCEDURE IF EXISTS sp_crear_prestamo;
DROP PROCEDURE IF EXISTS sp_registrar_devolucion;
DROP PROCEDURE IF EXISTS sp_obtener_prestamos_activos;
DROP PROCEDURE IF EXISTS sp_actualizar_prestamos_vencidos;

DROP PROCEDURE IF EXISTS sp_generar_multa;
DROP PROCEDURE IF EXISTS sp_pagar_multa;

DROP PROCEDURE IF EXISTS sp_obtener_estadisticas;
DROP PROCEDURE IF EXISTS sp_guardar_encuesta;
DROP PROCEDURE IF EXISTS sp_guardar_config_ui;
DROP PROCEDURE IF EXISTS sp_restaurar_datos_ejemplo;

-- =====================================================================
-- INICIO DE CREACIÓN DE PROCEDIMIENTOS ALMACENADOS
-- =====================================================================
DELIMITER //

-- ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
-- BLOQUE 1: PROCEDIMIENTOS QUE ESTÁN OK (SIN CAMBIOS)
-- ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

-- 1. Registrar Usuario
CREATE PROCEDURE sp_registrar_usuario(
    IN p_username VARCHAR(50), IN p_password_hash VARCHAR(255), IN p_email VARCHAR(100), IN p_rol VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    INSERT INTO usuarios (username, password_hash, email, rol) VALUES (p_username, p_password_hash, p_email, p_rol);
    COMMIT;
END //

-- 2. Login (Acepta usuario o email)
CREATE PROCEDURE sp_obtener_usuario_login(IN p_identificador VARCHAR(100))
BEGIN
    SELECT id, username, password_hash, rol, mfa_secret, activo, email
    FROM usuarios WHERE username = p_identificador OR email = p_identificador;
END //

-- 3. Actualizar MFA
CREATE PROCEDURE sp_actualizar_mfa_secret(IN p_usuario_id INT, IN p_mfa_secret VARCHAR(32))
BEGIN
    UPDATE usuarios SET mfa_secret = p_mfa_secret WHERE id = p_usuario_id;
END //

-- 4. Auditoría
CREATE PROCEDURE sp_registrar_auditoria(
    IN p_usuario_id INT, IN p_accion VARCHAR(100), IN p_detalles TEXT, IN p_ip VARCHAR(45)
)
BEGIN
    INSERT INTO auditoria (usuario_id, accion, detalles, ip_origen) VALUES (p_usuario_id, p_accion, p_detalles, p_ip);
END //

-- 5. Obtener Usuarios (Para el Panel de Admin)
CREATE PROCEDURE sp_obtener_usuarios()
BEGIN
    SELECT id, username, email, rol, activo, fecha_registro FROM usuarios ORDER BY fecha_registro DESC;
END //

-- 6. Crear Préstamo (Transacción de Stock)
CREATE PROCEDURE sp_crear_prestamo(
    IN p_libro_id INT, IN p_usuario_id INT, IN p_nombre_lector VARCHAR(100),
    IN p_fecha_prestamo DATE, IN p_fecha_vencimiento DATE, OUT p_mensaje VARCHAR(100)
)
BEGIN
    DECLARE v_stock INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; SET p_mensaje = 'ERROR: Fallo en la transacción.'; END;
    START TRANSACTION;
    SELECT ejemplares_disponibles INTO v_stock FROM libros WHERE id = p_libro_id FOR UPDATE;
    IF v_stock > 0 THEN
        INSERT INTO prestamos (libro_id, usuario_id, nombre_lector, fecha_prestamo, fecha_vencimiento, estado)
        VALUES (p_libro_id, p_usuario_id, p_nombre_lector, p_fecha_prestamo, p_fecha_vencimiento, 'Activo');
        UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE id = p_libro_id;
        COMMIT;
        SET p_mensaje = 'OK: Préstamo registrado exitosamente.';
    ELSE
        ROLLBACK;
        SET p_mensaje = 'ERROR: No hay ejemplares disponibles.';
    END IF;
END //

-- 7. Registrar Devolución
CREATE PROCEDURE sp_registrar_devolucion(IN p_prestamo_id INT)
BEGIN
    DECLARE v_libro_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    SELECT libro_id INTO v_libro_id FROM prestamos WHERE id = p_prestamo_id AND estado != 'Devuelto';
    UPDATE prestamos SET estado = 'Devuelto', fecha_devolucion = CURDATE() WHERE id = p_prestamo_id;
    UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles + 1 WHERE id = v_libro_id;
    COMMIT;
END //

-- 8. Obtener Préstamos Activos/Vencidos
CREATE PROCEDURE sp_obtener_prestamos_activos()
BEGIN
    SELECT p.id, l.titulo, p.nombre_lector, p.fecha_prestamo, p.fecha_vencimiento,
           DATEDIFF(CURDATE(), p.fecha_vencimiento) AS dias_retraso, p.estado
    FROM prestamos p
    JOIN libros l ON p.libro_id = l.id
    WHERE p.estado IN ('Activo', 'Vencido')
    ORDER BY p.fecha_vencimiento ASC;
END //

-- 9. Actualizar Préstamos Vencidos
CREATE PROCEDURE sp_actualizar_prestamos_vencidos()
BEGIN
    UPDATE prestamos SET estado = 'Vencido' WHERE estado = 'Activo' AND fecha_vencimiento < CURDATE();
END //

-- 10. Generar Multa
CREATE PROCEDURE sp_generar_multa(
    IN p_prestamo_id INT, IN p_valor_dia DECIMAL(10,2), IN p_recargo_porcentaje DECIMAL(5,2)
)
BEGIN
    DECLARE v_dias_retraso INT;
    DECLARE v_monto DECIMAL(10,2);
    SELECT DATEDIFF(CURDATE(), fecha_vencimiento) INTO v_dias_retraso FROM prestamos WHERE id = p_prestamo_id AND estado = 'Vencido';
    IF v_dias_retraso > 0 THEN
        SET v_monto = (v_dias_retraso * p_valor_dia) + ((v_dias_retraso * p_valor_dia) * (p_recargo_porcentaje / 100));
        INSERT INTO multas (prestamo_id, monto_total, dias_retraso) VALUES (p_prestamo_id, v_monto, v_dias_retraso)
        ON DUPLICATE KEY UPDATE monto_total = v_monto, dias_retraso = v_dias_retraso;
    END IF;
END //

-- 11. Pagar Multa
CREATE PROCEDURE sp_pagar_multa(IN p_multa_id INT)
BEGIN
    UPDATE multas SET pagada = TRUE WHERE id = p_multa_id;
END //

-- 12. Guardar Encuesta
CREATE PROCEDURE sp_guardar_encuesta(
    IN p_usuario_id INT, IN p_calificacion TINYINT, IN p_servicios VARCHAR(255), IN p_recomendacion TINYINT, IN p_comentarios TEXT
)
BEGIN
    INSERT INTO encuestas (usuario_id, calificacion, servicios_usados, probabilidad_recomendar, comentarios)
    VALUES (p_usuario_id, p_calificacion, p_servicios, p_recomendacion, p_comentarios);
END //

-- 13. Guardar Configuración UI
CREATE PROCEDURE sp_guardar_config_ui(
    IN p_usuario_id INT, IN p_color VARCHAR(7), IN p_fuente INT, IN p_modo_oscuro BOOLEAN
)
BEGIN
    INSERT INTO configuracion_ui (usuario_id, color_acento, tamano_fuente, modo_oscuro)
    VALUES (p_usuario_id, p_color, p_fuente, p_modo_oscuro)
    ON DUPLICATE KEY UPDATE color_acento = p_color, tamano_fuente = p_fuente, modo_oscuro = p_modo_oscuro;
END //


-- ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
-- BLOQUE 2: PROCEDIMIENTOS AJUSTADOS (BORRADO LÓGICO Y FILTROS)
-- ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

-- 14. Crear Libro
CREATE PROCEDURE sp_crear_libro(
    IN p_titulo VARCHAR(150), IN p_autor VARCHAR(100), IN p_isbn VARCHAR(13), IN p_anio YEAR,
    IN p_ejemplares INT, IN p_categoria_id INT, IN p_formato VARCHAR(10), IN p_sinopsis TEXT, IN p_etiquetas VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    INSERT INTO libros (titulo, autor, isbn, anio_publicacion, ejemplares_totales, ejemplares_disponibles, categoria_id, formato, sinopsis, etiquetas)
    VALUES (p_titulo, p_autor, p_isbn, p_anio, p_ejemplares, p_ejemplares, p_categoria_id, p_formato, p_sinopsis, p_etiquetas);
    COMMIT;
END //

-- 15. Obtener Libros (Ajustado: Solo activos)
CREATE PROCEDURE sp_obtener_libros()
BEGIN
    SELECT l.id, l.titulo, l.autor, l.isbn, l.anio_publicacion, l.ejemplares_totales,
           l.ejemplares_disponibles, l.formato, c.nombre AS categoria, l.sinopsis, l.etiquetas
    FROM libros l
    LEFT JOIN categorias c ON l.categoria_id = c.id
    WHERE l.activo = TRUE
    ORDER BY l.titulo ASC;
END //

-- 16. Buscar Libros (Ajustado: Filtro activo + 3 parámetros)
CREATE PROCEDURE sp_buscar_libros(
    IN p_termino VARCHAR(100), IN p_categoria_id INT, IN p_solo_disponibles BOOLEAN
)
BEGIN
    SELECT l.id, l.titulo, l.autor, l.isbn, l.anio_publicacion,
           l.ejemplares_disponibles, l.ejemplares_totales, c.nombre AS categoria
    FROM libros l
    LEFT JOIN categorias c ON l.categoria_id = c.id
    WHERE l.activo = TRUE
    AND (l.titulo LIKE CONCAT('%', p_termino, '%') OR l.autor LIKE CONCAT('%', p_termino, '%'))
    AND (p_categoria_id IS NULL OR p_categoria_id = 0 OR l.categoria_id = p_categoria_id)
    AND (p_solo_disponibles = FALSE OR l.ejemplares_disponibles > 0)
    ORDER BY l.titulo ASC;
END //

-- 17. Actualizar Libro
CREATE PROCEDURE sp_actualizar_libro(
    IN p_id INT, IN p_titulo VARCHAR(150), IN p_autor VARCHAR(100), IN p_categoria_id INT, IN p_sinopsis TEXT
)
BEGIN
    UPDATE libros SET titulo = p_titulo, autor = p_autor, categoria_id = p_categoria_id, sinopsis = p_sinopsis WHERE id = p_id;
END //

-- 18. Eliminar Libro (Ajustado: Borrado Lógico, 1 solo parámetro)
CREATE PROCEDURE sp_eliminar_libro(IN p_id INT)
BEGIN
    UPDATE libros SET activo = FALSE WHERE id = p_id;
END //

-- 19. Obtener Categorías
CREATE PROCEDURE sp_obtener_categorias()
BEGIN
    SELECT id, nombre FROM categorias ORDER BY nombre ASC;
END //

-- 20. Obtener Estadísticas (Ajustado: Solo cuenta activos)
CREATE PROCEDURE sp_obtener_estadisticas()
BEGIN
    SELECT
        (SELECT COUNT(*) FROM libros WHERE activo = TRUE) AS total_titulos,
        (SELECT SUM(ejemplares_disponibles) FROM libros WHERE activo = TRUE) AS ejemplares_disponibles,
        (SELECT COUNT(*) FROM prestamos WHERE estado = 'Activo') AS prestamos_activos,
        (SELECT COUNT(*) FROM prestamos WHERE estado = 'Vencido') AS prestamos_vencidos;
END //

-- 21. Restaurar Datos de Ejemplo (Ajustado: chequea solo activos)
CREATE PROCEDURE sp_restaurar_datos_ejemplo()
BEGIN
    DECLARE v_user_id INT;
    IF (SELECT COUNT(*) FROM libros WHERE activo = TRUE) = 0 THEN
        INSERT INTO categorias (nombre) VALUES ('Literatura'), ('Ciencias'), ('Historia'), ('Arte');
        INSERT INTO libros (titulo, autor, isbn, anio_publicacion, ejemplares_totales, ejemplares_disponibles, categoria_id, formato)
        VALUES
        ('Cien años de soledad', 'Gabriel García Márquez', '9780307474728', 1967, 3, 3, 1, 'Físico'),
        ('Breve historia del tiempo', 'Stephen Hawking', '9788498921991', 1988, 2, 2, 2, 'Digital'),
        ('La vorágine', 'José Eustasio Rivera', '9789583002570', 1924, 1, 1, 1, 'Físico'),
        ('Historia del arte', 'Ernst Gombrich', '9780714832470', 1950, 2, 2, 4, 'Físico');
        SELECT id INTO v_user_id FROM usuarios LIMIT 1;
        IF v_user_id IS NOT NULL THEN
            INSERT INTO prestamos (libro_id, usuario_id, nombre_lector, fecha_prestamo, fecha_vencimiento, estado)
            VALUES (1, v_user_id, 'Laura Martínez', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Activo');
            UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE id = 1;
            INSERT INTO prestamos (libro_id, usuario_id, nombre_lector, fecha_prestamo, fecha_vencimiento, estado)
            VALUES (3, v_user_id, 'Andrés Rojas', DATE_SUB(CURDATE(), INTERVAL 12 DAY), DATE_SUB(CURDATE(), INTERVAL 4 DAY), 'Vencido');
            UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE id = 3;
        END IF;
    END IF;
END //

DELIMITER ;

SHOW CREATE PROCEDURE sp_eliminar_libro;

select * from libros;
select * from auditoria;
select * from encuestas;

CREATE TABLE IF NOT EXISTS progreso_retos (
    usuario_id INT,
    reto_id INT,
    completado BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (usuario_id, reto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);


DROP PROCEDURE IF EXISTS sp_obtener_progreso_retos;
DELIMITER //
CREATE PROCEDURE sp_obtener_progreso_retos(IN p_usuario_id INT)
BEGIN
    SELECT reto_id, completado FROM progreso_retos WHERE usuario_id = p_usuario_id;
END //
DELIMITER ;

-- 3. SP para actualizar (marcar/desmarcar) un reto
DROP PROCEDURE IF EXISTS sp_actualizar_reto;
DELIMITER //
CREATE PROCEDURE sp_actualizar_reto(
    IN p_usuario_id INT,
    IN p_reto_id INT,
    IN p_completado BOOLEAN
)
BEGIN
    INSERT INTO progreso_retos (usuario_id, reto_id, completado)
    VALUES (p_usuario_id, p_reto_id, p_completado)
    ON DUPLICATE KEY UPDATE completado = p_completado;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_obtener_config_ui(IN p_usuario_id INT)
BEGIN
    SELECT color_acento, tamano_fuente, modo_oscuro
    FROM configuracion_ui
    WHERE usuario_id = p_usuario_id;
END //
DELIMITER ;