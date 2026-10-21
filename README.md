<div align="center">
  <h1>📚 Biblioteca del Campus - Sistema de Gestión Integral</h1>
  <p>Un sistema de escritorio profesional, seguro y escalable para la administración de bibliotecas universitarias.</p>

  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/Database-MySQL%208.0-orange?style=for-the-badge&logo=mysql" alt="MySQL">
  <img src="https://img.shields.io/badge/Architecture-Clean%20%7C%203--Tier-red?style=for-the-badge" alt="Arquitectura">
  <img src="https://img.shields.io/badge/Security-ISO%2027001%20%7C%20MFA-black?style=for-the-badge" alt="Seguridad">
</div>

<br>

## 📖 Tabla de Contenidos
1. [Introducción y Propósito](#-introducción-y-propósito)
2. [Características Principales](#-características-principales)
3. [Arquitectura Limpia (Explicada para principiantes)](#-arquitectura-limpia-explicada-para-principiantes)
4. [Seguridad y Normativas (ISO)](#-seguridad-y-normativas-iso)
5. [Diseño de la Base de Datos](#-diseño-de-la-base-de-datos)
6. [Requisitos e Instalación Paso a Paso](#-requisitos-e-instalación-paso-a-paso)
7. [Guía de Uso del Sistema](#-guía-de-uso-del-sistema)
8. [Solución de Problemas Comunes (Troubleshooting)](#-solución-de-problemas-comunes-troubleshooting)
9. [Autor y Agradecimientos](#-autor-y-agradecimientos)

---

## 🚀 Introducción y Propósito

**Biblioteca del Campus** es una aplicación de escritorio de nivel empresarial desarrollada en Python. No es un simple CRUD; es un sistema diseñado bajo estrictos estándares de ingeniería de software para demostrar cómo se construye una aplicación real, segura y mantenible.

El proyecto nace con el objetivo de digitalizar la gestión de una biblioteca universitaria, controlando desde el acceso de los usuarios (con doble factor de autenticación) hasta el préstamo de libros, cálculo de multas y personalización visual de la interfaz.

---

## ✨ Características Principales

### 🔐 Módulo de Seguridad y Acceso
*   **Hashing de Contraseñas:** Uso de `Bcrypt` para garantizar que las contraseñas nunca se guarden en texto plano.
*   **Autenticación de Doble Factor (MFA):** Integración nativa con estándar TOTP (Google Authenticator / Authy) sin costos externos.
*   **Control de Acceso Basado en Roles (RBAC):** Los usuarios pueden ser `ADMIN`, `BIBLIOTECARIO` o `ESTUDIANTE`. El menú se adapta dinámicamente según el rol.
*   **Auditoría Forense:** Cada acción (login, préstamo, creación de libro, cierre de sesión) queda registrada en la base de datos con la IP y el ID del usuario.

### 📚 Módulo de Catálogo
*   **Registro Completo:** Formulario con validaciones estrictas (ISBN de 13 dígitos, stock, categorías, formatos).
*   **Búsqueda Dinámica:** Filtros en tiempo real por título, autor, categoría y disponibilidad.
*   **Borrado Lógico (Soft Delete):** Los libros no se eliminan de la base de datos para no romper el historial; simplemente pasan a un estado "inactivo".

### 🔄 Módulo de Préstamos y Multas
*   **Gestión de Stock Automático:** Al prestar un libro, el stock baja; al devolverlo, sube.
*   **Fechas Inteligentes:** Cálculo automático de la fecha de devolución (8 días para estudiantes, 15 para docentes).
*   **Tarjetas de Préstamos Visuales:** Interfaz gráfica que resalta en rojo los préstamos vencidos y en verde los activos.
*   **Calculadora de Multas Interactiva:** Un módulo visual que permite calcular el valor a pagar por días de retraso, con recargos por reincidencia.

### 🎨 Módulo de Interfaz y Personalización
*   **Diseño Moderno:** Inspirado en interfaces web modernas, usando `ttk` para un look limpio.
*   **Modo Oscuro/Claro:** El usuario puede alternar entre temas visuales en tiempo real.
*   **Persistencia de Preferencias:** El color de acento y el modo oscuro elegidos por el usuario se guardan en la base de datos y se aplican en el próximo inicio de sesión.

---

## 🏗️ Arquitectura Limpia (Explicada para principiantes)

Si estás empezando, este es el apartado más importante. El proyecto usa **Clean Architecture (Arquitectura Limpia de 3 Capas)**. Esto significa que el código está separado por "responsabilidades", como si fueran las capas de una cebolla:

```text
BIBLIOTECA_xXxCASTILLO/
│
├── config/          # ⚙️ INFRAESTRUCTURA: Variables de entorno y Docker Manager.
├── database/        # 🗄️ PERSISTENCIA: Conexión a MySQL y Scripts SQL (.sql).
├── security/        # 🛡️ SEGURIDAD: Lógica de hashing, MFA y registro de auditoría.
├── ui/              # 🎨 PRESENTACIÓN: Todo lo visual (Vistas, Estilos, Controladores).
└── main.py          # 🚀 PUNTO DE ENTRADA: Inicia la aplicación.

```
---

### FRACCIÓN 3: Normativas ISO, Base de Datos e Instalación
Copia esto y pégalo debajo de la Fracción 2:

```markdown
## 🛡️ Seguridad y Normativas ISO

Este proyecto fue diseñado pensando en estándares reales de la industria:

*   **ISO/IEC 25010 (Calidad):** Separación de responsabilidades, código modular y manejo de excepciones robusto.
*   **ISO/IEC 27001 (Seguridad de la Información):** Ninguna contraseña se guarda en texto plano. El control de acceso está estrictamente limitado por roles. **Cero consultas SQL directas en Python** (todo se hace con Procedimientos Almacenados para evitar Inyección SQL).
*   **ISO/IEC 27035 (Gestión de Incidentes):** Si la base de datos se cae, el sistema no colapsa. Se registra el error y se aplican transacciones (`ROLLBACK`) para no dejar datos corruptos.
```
---

## 🗄️ Diseño de la Base de Datos

La base de datos (`biblioteca_db`) contiene las siguientes tablas principales:
*   `usuarios`: Almacena credenciales, roles y secretos MFA.
*   `libros` y `categorias`: El inventario de la biblioteca.
*   `prestamos`: Registro histórico de salidas y devoluciones.
*   `multas`: Cálculos de penalizaciones por retrasos.
*   `auditoria`: Bitácora de todos los movimientos del sistema.
*   `configuracion_ui`: Preferencias visuales por usuario (modo oscuro, colores).
*   `encuestas`: Feedback de los usuarios.

**Uso de Procedimientos Almacenados (Stored Procedures):**
Toda la lógica de negocio (crear préstamo, registrar devolución, generar multa) está encapsulada en MySQL. Python solo envía instrucciones como `CALL sp_crear_prestamo(...)`. Esto hace que el sistema sea **prácticamente invulnerable a ataques de inyección**.

---

## 💻 Requisitos e Instalación Paso a Paso

### Prerrequisitos
*   Tener instalado **Python 3.10** o superior.
*   Tener instalado **MySQL 8.0** (o Docker en su defecto).
*   Tener instalado **Git** para clonar el repositorio.

### Paso 1: Clonar el proyecto
Abre tu terminal o consola y ejecuta:
```bash
git clone https://github.com/TU_USUARIO/BIBLIOTECA_xXxCASTILLO.git
cd BIBLIOTECA_xXxCASTILLO
```
---

### Paso 2: Crear el Entorno Virtual
```bash
# En Windows:
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```
---

### Paso 3: Instalar Dependencias
Con el entorno virtual activo, ejecuta:
```bash
pip install -r requirements.txt
```
---

### Paso 4: Configurar la Base de Datos
1. Abre MySQL Workbench (o cualquier gestor de MySQL).
2. Crea una conexión local.
3. Abre una nueva pestaña de query (consulta) y ejecuta el archivo database/scripts/init.sql. Este script creará todas las tablas necesarias.
4. Abre otra pestaña y ejecuta el archivo database/scripts/stored_procedures.sql. Este script creará los +20 Procedimientos Almacenados.

---

### Paso 5: Configurar Credenciales (Opcional)
Si tu usuario de MySQL no es root o tu contraseña es diferente, edita el archivo config/env.py
```bash
DB_USER = "tu_usuario"
DB_PASSWORD = "tu_contraseña"txt
```
---

### Paso 6: Ejecutar la Aplicación
```bash
python main.py
```

---

### FRACCIÓN 4: Guía de Uso, Troubleshooting y Autor



## 🖥️ Guía de Uso del Sistema

1. **Registro / Login:** Al iniciar, puedes registrarte como estudiante o usar las credenciales de administrador creadas en la base de datos. Si activas el MFA, se te pedirá un código de 6 dígitos.
2. **Dashboard (Inicio):** Verás un resumen de estadísticas (total de libros, préstamos activos, vencidos). Puedes usar el botón "Restaurar datos de ejemplo" para poblar la base de datos rápidamente.
3. **Catálogo:** Haz clic en "Registrar Libro" para añadir libros. Usa la barra de búsqueda para filtrar en tiempo real. Si seleccionas un libro, puedes "Prestarlo" (te redirige al formulario con los datos ya cargados) o "Dar de Baja" (borrado lógico).
4. **Préstamos:** Ve a "Nuevo Préstamo", selecciona un libro, un nombre de lector y un correo institucional válido (`@universidad.edu.co`). El sistema calcula la fecha de devolución automáticamente. En "Préstamos Activos", verás tarjetas de colores; haz clic en "Registrar devolución" para liberar el libro.
5. **Personalizar Apariencia:** Ve al menú lateral, cambia el color de acento y activa el Modo Oscuro. ¡Verás cómo toda la interfaz cambia al instante!

---

## 🚑 Solución de Problemas Comunes (Troubleshooting)

Si eres nuevo en Python, es posible que te encuentres con estos errores. Aquí te decimos cómo solucionarlos:

*   **Error: `ModuleNotFoundError: No module named 'database'`**
    *   *Causa:* Python no reconoce las carpetas.
    *   *Solución:* Asegúrate de haber creado los archivos `__init__.py` (vacíos) dentro de cada carpeta (`config`, `database`, `security`, `ui`). En PyCharm, haz clic derecho en la carpeta raíz y selecciona `Mark Directory as -> Sources Root`.
*   **Error: `1049 (42000): Unknown database 'biblioteca_db'`**
    *   *Causa:* No has ejecutado el script `init.sql` en MySQL.
    *   *Solución:* Abre MySQL Workbench y ejecuta el script como se indica en el Paso 4.
*   **Error: `1318 (42000): Incorrect number of arguments`**
    *   *Causa:* El Procedimiento Almacenado en MySQL está desactualizado.
    *   *Solución:* Vuelve a ejecutar el archivo `stored_procedures.sql` completo para actualizar todos los SPs.
*   **La ventana de Tkinter se ve anticuada o los colores no cambian:**
    *   *Causa:* El tema de Tkinter no se cargó bien.
    *   *Solución:* Asegúrate de que en tu archivo `main.py` estés llamando a `Theme.aplicar_estilos(root)` antes de cargar las vistas.

---

## 👨‍💻 Autor y Agradecimientos

Desarrollado con pasión por **Xavier Castillo**.
*   **LinkedIn:** [LinkedIn](https://www.linkedin.com/in/xavier-alberto-castillo-varon-a540a1287/?isSelfProfile=true)
*   **GitHub:** [Xavier Castillo](https://github.com/castilloxavie)

*Este proyecto fue construido como un ejercicio práctico de Ingeniería de Software Avanzada, aplicando Arquitectura Limpia, DevOps (Docker), Ciberseguridad (MFA, Bcrypt) y normativas ISO. Si estás aprendiendo, siéntete libre de clonarlo, estudiarlo y mejorarlo.*