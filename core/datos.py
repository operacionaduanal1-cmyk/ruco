"""
RUCO - Capa de datos.
Se conecta a Turso (nube) cuando hay credenciales en Streamlit.
Si no las hay (entorno de prueba), usa SQLite local automáticamente.
Una capa de compatibilidad hace que el resto del codigo funcione igual
con ambos motores (Turso via libsql-client, o SQLite local).
"""
import hashlib
import os
from datetime import datetime

def _credenciales_turso():
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

# ---- Cliente Turso (se crea una sola vez) ----
_turso_client = None
def _get_turso():
    global _turso_client
    if _turso_client is None:
        import libsql_client
        url, token = _credenciales_turso()
        url_http = url.replace("libsql://", "https://")
        _turso_client = libsql_client.create_client_sync(url=url_http, auth_token=token)
    return _turso_client

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Ejecucion unificada ----
def _exec(sql, params=()):
    """Ejecuta una sentencia. Devuelve (filas_como_dict, lastrowid)."""
    if _es_turso():
        client = _get_turso()
        # libsql-client usa ? como placeholders, igual que sqlite
        rs = client.execute(sql, list(params))
        cols = rs.columns if rs.columns else []
        filas = [dict(zip(cols, row)) for row in rs.rows]
        last = rs.last_insert_rowid if hasattr(rs, "last_insert_rowid") else None
        return filas, last
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "ruco.db")
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(sql, params)
        filas = [dict(r) for r in cur.fetchall()] if cur.description else []
        last = cur.lastrowid
        con.commit()
        con.close()
        return filas, last

def inicializar():
    _exec("""CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL)""")
    _exec("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL,
        cliente_ligado TEXT,
        activo INTEGER DEFAULT 1,
        creado TEXT)""")
    _exec("""CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla TEXT, registro_id INTEGER, usuario TEXT,
        campo TEXT, valor_anterior TEXT, valor_nuevo TEXT, fecha TEXT)""")

    roles_base = ["Administrador", "Operaciones", "Finanzas", "Captura",
                  "Gestión/Reportes", "Consulta interna", "Consulta cliente"]
    for r in roles_base:
        _exec("INSERT OR IGNORE INTO roles (nombre) VALUES (?)", (r,))

    filas, _ = _exec("SELECT COUNT(*) AS n FROM usuarios WHERE rol='Administrador'")
    if filas and filas[0]["n"] == 0:
        _exec("""INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo, creado)
                 VALUES (?,?,?,?,1,?)""",
              ("Administrador RUCO", "admin", hash_password("admin123"),
               "Administrador", datetime.now().isoformat()))

def autenticar(usuario, password):
    filas, _ = _exec(
        "SELECT * FROM usuarios WHERE usuario=? AND password_hash=? AND activo=1",
        (usuario.strip().lower(), hash_password(password)))
    return filas[0] if filas else None

def listar_usuarios():
    filas, _ = _exec("SELECT * FROM usuarios ORDER BY activo DESC, nombre")
    return filas

def listar_roles():
    filas, _ = _exec("SELECT nombre FROM roles ORDER BY id")
    return [f["nombre"] for f in filas]

def crear_usuario(nombre, usuario, password, rol, cliente_ligado, admin_actor):
    existe, _ = _exec("SELECT id FROM usuarios WHERE usuario=?", (usuario.strip().lower(),))
    if existe:
        return False, "Ese nombre de usuario ya existe."
    _exec("""INSERT INTO usuarios (nombre, usuario, password_hash, rol, cliente_ligado, activo, creado)
             VALUES (?,?,?,?,?,1,?)""",
          (nombre.strip(), usuario.strip().lower(), hash_password(password),
           rol, cliente_ligado or None, datetime.now().isoformat()))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('usuarios',0,?,?,?,?,?)""",
          (admin_actor, "alta", "", f"{nombre} ({rol})", datetime.now().isoformat()))
    return True, "Usuario creado."

def cambiar_estado_usuario(uid, activo, admin_actor):
    prev, _ = _exec("SELECT activo FROM usuarios WHERE id=?", (uid,))
    pact = prev[0]["activo"] if prev else ""
    _exec("UPDATE usuarios SET activo=? WHERE id=?", (1 if activo else 0, uid))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('usuarios',?,?,?,?,?,?)""",
          (uid, admin_actor, "activo", str(pact), str(1 if activo else 0), datetime.now().isoformat()))

def historial_reciente(limite=50):
    filas, _ = _exec("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,))
    return filas
