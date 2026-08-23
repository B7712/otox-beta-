import os
import sqlite3

# Intentamos importar libsql para cuando estemos en producción (Turso)
try:
    import libsql_experimental as libsql
    HAS_LIBSQL = True
except ImportError:
    HAS_LIBSQL = False

DATABASE_NAME = "otox.db"

def obtener_conexion():
    """
    Crea y retorna una conexión a la base de datos.
    Usa Turso en Render si las variables existen, o SQLite local en PC/Termux.
    """
    turso_url = os.environ.get("TURSO_DATABASE_URL")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN")

    # Si estamos en Render y tenemos las credenciales de Turso
    if HAS_LIBSQL and turso_url and turso_token:
        conn = libsql.connect(database=turso_url, auth_token=turso_token)
        # Nota: libsql maneja sus propios tipos de fábrica de filas
        return conn

    # Conexión local tradicional con SQLite[cite: 1]
    conn = sqlite3.connect(DATABASE_NAME)[cite: 1]
    conn.row_factory = sqlite3.Row[cite: 1]
    return conn

def inicializar_bd():
    """Crea la estructura de tablas inicial si no existen."""
    conn = obtener_conexion()
    cursor = conn.cursor()

    # 1. TABLA USUARIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            handle TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            bio TEXT,
            foto_avatar TEXT,
            banner_url TEXT,
            tema TEXT DEFAULT 'oscuro'
        )
    ''')

    # 2. TABLA POSTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            media_url TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    # 3. TABLA ESTUDIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    # 4. TABLA CAPITULOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capitulos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudio_id INTEGER NOT NULL,
            numero INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            explicacion TEXT,
            media_url TEXT,
            FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE CASCADE
        )
    ''')

    # 5. TABLA COMENTARIOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            post_id INTEGER,
            estudio_id INTEGER,
            texto TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE CASCADE
        )
    ''')

    # 6. TABLA RESPUESTAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comentario_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            texto TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comentario_id) REFERENCES comentarios (id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    # 7. TABLA LIKES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            post_id INTEGER,
            estudio_id INTEGER,
            comentario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE CASCADE,
            FOREIGN KEY (comentario_id) REFERENCES comentarios (id) ON DELETE CASCADE
        )
    ''')

    # 8. TABLA SEGUIDORES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguidores (
            seguidor_id INTEGER NOT NULL,
            seguido_id INTEGER NOT NULL,
            PRIMARY KEY (seguidor_id, seguido_id),
            FOREIGN KEY (seguidor_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (seguido_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')

    # 9. TABLA ESTUDIOS FAVORITOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudios_favoritos (
            usuario_id INTEGER NOT NULL,
            estudio_id INTEGER NOT NULL,
            PRIMARY KEY (usuario_id, estudio_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()

    # Cargar usuario inicial si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (nombre, handle, email, password, bio, foto_avatar, banner_url, tema)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "DevMúsica Master",
            "prueba_de_perfil",
            "usuario@otox.com",
            "password123",
            "Productor y compositor 🎹🔥 | Creando synthwave en Otox.",
            "",
            "",
            "oscuro"
        ))
        conn.commit()

    conn.close()

if __name__ == '__main__':
    inicializar_bd()
    print("¡Base de datos Otox reinicializada correctamente! 🚀")
