"""
RUCO - Capa de datos.
Por ahora usa SQLite local para que veas todo funcionando sin riesgo.
Cuando valides el diseño, esta MISMA estructura se conecta a tu Turso de trabajo
(Turso habla el mismo idioma que SQLite, así que la migración es directa).
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ruco.db")

def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def hash_password(password: str) -> str:
    """Guardamos la contraseña cifrada, nunca en texto plano."""
    return hashlib.sha256(password.encode()).hexdigest()

def inicializar():
    """Crea las tablas si no existen y siembra el primer administrador."""
    con = conectar()
    c = con.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            cliente_ligado TEXT,
            activo INTEGER DEFAULT 1,
            creado TEXT
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabla TEXT,
            registro_id INTEGER,
            usuario TEXT,
            campo TEXT,
            valor_anterior TEXT,
            valor_nuevo TEXT,
            fecha TEXT
        )""")

    # Roles base
    roles_base = ["Administrador", "Operaciones", "Finanzas", "Captura",
                  "Gestión/Reportes", "Consulta interna", "Consulta cliente"]
    for r in roles_base:
        c.execute("INSERT OR IGNORE INTO roles (nombre) VALUES (?)", (r,))

    # Sembrar el primer admin (huevo y gallina): solo si no hay ningún admin
    c.execute("SELECT COUNT(*) FROM usuarios WHERE rol='Administrador'")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo, creado)
                     VALUES (?,?,?,?,1,?)""",
                  ("Administrador RUCO", "admin", hash_password("admin123"),
                   "Administrador", datetime.now().isoformat()))

    con.commit()
    con.close()

# --- Autenticación ---
def autenticar(usuario: str, password: str):
    con = conectar()
    c = con.cursor()
    c.execute("""SELECT * FROM usuarios WHERE usuario=? AND password_hash=? AND activo=1""",
              (usuario.strip(), hash_password(password)))
    fila = c.fetchone()
    con.close()
    return dict(fila) if fila else None

# --- Gestión de usuarios ---
def listar_usuarios():
    con = conectar()
    filas = con.execute("SELECT * FROM usuarios ORDER BY activo DESC, nombre").fetchall()
    con.close()
    return [dict(f) for f in filas]

def listar_roles():
    con = conectar()
    filas = con.execute("SELECT nombre FROM roles ORDER BY id").fetchall()
    con.close()
    return [f["nombre"] for f in filas]

def crear_usuario(nombre, usuario, password, rol, cliente_ligado, admin_actor):
    con = conectar()
    c = con.cursor()
    try:
        c.execute("""INSERT INTO usuarios (nombre, usuario, password_hash, rol, cliente_ligado, activo, creado)
                     VALUES (?,?,?,?,?,1,?)""",
                  (nombre.strip(), usuario.strip().lower(), hash_password(password),
                   rol, cliente_ligado or None, datetime.now().isoformat()))
        nuevo_id = c.lastrowid
        c.execute("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
                     VALUES ('usuarios',?,?,?,?,?,?)""",
                  (nuevo_id, admin_actor, "alta", "", f"{nombre} ({rol})", datetime.now().isoformat()))
        con.commit()
        return True, "Usuario creado."
    except sqlite3.IntegrityError:
        return False, "Ese nombre de usuario ya existe."
    finally:
        con.close()

def cambiar_estado_usuario(uid, activo, admin_actor):
    con = conectar()
    c = con.cursor()
    prev = c.execute("SELECT activo, nombre FROM usuarios WHERE id=?", (uid,)).fetchone()
    c.execute("UPDATE usuarios SET activo=? WHERE id=?", (1 if activo else 0, uid))
    c.execute("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
                 VALUES ('usuarios',?,?,?,?,?,?)""",
              (uid, admin_actor, "activo", str(prev["activo"]), str(1 if activo else 0),
               datetime.now().isoformat()))
    con.commit()
    con.close()

def historial_reciente(limite=50):
    con = conectar()
    filas = con.execute("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
    con.close()
    return [dict(f) for f in filas]
