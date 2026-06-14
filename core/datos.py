"""
RUCO - Capa de datos.
Se conecta a Turso (nube) cuando hay credenciales en Streamlit.
Si no las hay (entorno de prueba), usa SQLite local automáticamente.
"""
import hashlib
import os
from datetime import datetime

def _credenciales_turso():
    """Lee las llaves de Turso del cofre de Streamlit o de variables de entorno."""
    try:
        import streamlit as st
        url = st.secrets.get("TURSO_URL", None)
        token = st.secrets.get("TURSO_TOKEN", None)
        if url and token:
            return url, token
    except Exception:
        pass
    url = os.environ.get("TURSO_URL")
    token = os.environ.get("TURSO_TOKEN")
    if url and token:
        return url, token
    return None, None

def _es_turso():
    u, t = _credenciales_turso()
    return bool(u and t)

def conectar():
    url, token = _credenciales_turso()
    if url and token:
        import libsql_experimental as libsql
        return libsql.connect(database=url, auth_token=token)
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "ruco.db")
    return sqlite3.connect(db_path)

# --- Helpers que funcionan igual en Turso y en SQLite local ---
def _ejecutar(sql, params=(), commit=False):
    """Ejecuta una sentencia. Devuelve el cursor."""
    con = conectar()
    cur = con.cursor()
    cur.execute(sql, params)
    if commit:
        con.commit()
    return con, cur

def _filas_dict(sql, params=()):
    """Devuelve una lista de diccionarios {columna: valor}."""
    con = conectar()
    cur = con.cursor()
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    filas = [dict(zip(cols, row)) for row in cur.fetchall()]
    con.close()
    return filas

def _una_fila_dict(sql, params=()):
    r = _filas_dict(sql, params)
    return r[0] if r else None

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def inicializar():
    """Crea las tablas si no existen y siembra el primer administrador."""
    con = conectar()
    c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL,
        cliente_ligado TEXT,
        activo INTEGER DEFAULT 1,
        creado TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla TEXT, registro_id INTEGER, usuario TEXT,
        campo TEXT, valor_anterior TEXT, valor_nuevo TEXT, fecha TEXT)""")

    roles_base = ["Administrador", "Operaciones", "Finanzas", "Captura",
                  "Gestión/Reportes", "Consulta interna", "Consulta cliente"]
    for r in roles_base:
        c.execute("INSERT OR IGNORE INTO roles (nombre) VALUES (?)", (r,))

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
    return _una_fila_dict(
        "SELECT * FROM usuarios WHERE usuario=? AND password_hash=? AND activo=1",
        (usuario.strip().lower(), hash_password(password)))

# --- Gestión de usuarios ---
def listar_usuarios():
    return _filas_dict("SELECT * FROM usuarios ORDER BY activo DESC, nombre")

def listar_roles():
    return [f["nombre"] for f in _filas_dict("SELECT nombre FROM roles ORDER BY id")]

def crear_usuario(nombre, usuario, password, rol, cliente_ligado, admin_actor):
    # Verificar duplicado primero (funciona igual en ambos motores)
    existe = _una_fila_dict("SELECT id FROM usuarios WHERE usuario=?", (usuario.strip().lower(),))
    if existe:
        return False, "Ese nombre de usuario ya existe."
    con = conectar()
    c = con.cursor()
    c.execute("""INSERT INTO usuarios (nombre, usuario, password_hash, rol, cliente_ligado, activo, creado)
                 VALUES (?,?,?,?,?,1,?)""",
              (nombre.strip(), usuario.strip().lower(), hash_password(password),
               rol, cliente_ligado or None, datetime.now().isoformat()))
    c.execute("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
                 VALUES ('usuarios',0,?,?,?,?,?)""",
              (admin_actor, "alta", "", f"{nombre} ({rol})", datetime.now().isoformat()))
    con.commit()
    con.close()
    return True, "Usuario creado."

def cambiar_estado_usuario(uid, activo, admin_actor):
    prev = _una_fila_dict("SELECT activo, nombre FROM usuarios WHERE id=?", (uid,))
    con = conectar()
    c = con.cursor()
    c.execute("UPDATE usuarios SET activo=? WHERE id=?", (1 if activo else 0, uid))
    c.execute("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
                 VALUES ('usuarios',?,?,?,?,?,?)""",
              (uid, admin_actor, "activo", str(prev["activo"] if prev else ""),
               str(1 if activo else 0), datetime.now().isoformat()))
    con.commit()
    con.close()

def historial_reciente(limite=50):
    return _filas_dict("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,))
