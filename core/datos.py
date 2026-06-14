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
        rs = client.execute(sql, list(params))
        filas = []
        try:
            cols = list(rs.columns) if getattr(rs, "columns", None) else []
            if cols:
                for row in rs.rows:
                    # cada row se puede indexar por posicion
                    filas.append({cols[i]: row[i] for i in range(len(cols))})
        except Exception:
            filas = []
        last = getattr(rs, "last_insert_rowid", None)
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

def eliminar_usuario(uid, admin_actor):
    """Borra un usuario por completo. No se puede deshacer."""
    prev, _ = _exec("SELECT usuario FROM usuarios WHERE id=?", (uid,))
    nombre = prev[0]["usuario"] if prev else str(uid)
    _exec("DELETE FROM usuarios WHERE id=?", (uid,))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('usuarios',?,?,?,?,?,?)""",
          (uid, admin_actor, "eliminado", nombre, "(borrado)", datetime.now().isoformat()))

def historial_reciente(limite=50):
    filas, _ = _exec("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,))
    return filas


# ============================================================
# CONTENEDORES
# ============================================================
def inicializar_contenedores():
    """Crea la tabla de contenedores si no existe."""
    _exec("""CREATE TABLE IF NOT EXISTS contenedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consecutivo TEXT,
        aduana TEXT NOT NULL,
        anio INTEGER,
        folio INTEGER,
        contenedor TEXT NOT NULL,
        aa TEXT,
        referencia TEXT,
        pedimento TEXT,
        fecha_pago TEXT,
        cliente TEXT,
        eta TEXT,
        estatus TEXT,
        importador TEXT,
        detalle TEXT,
        regimen TEXT,
        observaciones TEXT,
        modulo_t3 TEXT,
        terminal TEXT,
        modalidad TEXT,
        revalidado TEXT,
        finanzas TEXT,
        liberacion TEXT,
        eir TEXT,
        ata TEXT,
        asignacion TEXT,
        ejecutivo TEXT,
        autorizacion TEXT,
        creado TEXT,
        creado_por TEXT,
        motivo_baja TEXT,
        activo INTEGER DEFAULT 1)""")
    # Asegurar columna motivo_baja si la tabla ya existía sin ella
    try:
        _exec("ALTER TABLE contenedores ADD COLUMN motivo_baja TEXT")
    except Exception:
        pass

def ultimo_folio(aduana, anio):
    """Devuelve el folio más alto usado en esa aduana ese año (0 si ninguno)."""
    filas, _ = _exec(
        "SELECT MAX(folio) AS m FROM contenedores WHERE aduana=? AND anio=?",
        (aduana, anio))
    if filas and filas[0].get("m") is not None:
        return int(filas[0]["m"])
    return 0

def buscar_contenedor_existente(contenedor_limpio):
    """Busca si un contenedor ya existe (en cualquier aduana). Devuelve la fila más reciente o None."""
    filas, _ = _exec(
        "SELECT * FROM contenedores WHERE contenedor=? ORDER BY id DESC LIMIT 1",
        (contenedor_limpio,))
    return filas[0] if filas else None

def crear_contenedor(aduana, contenedor_limpio, cliente, consecutivo, anio, folio, actor):
    """Crea un contenedor con lo mínimo. Estatus inicial CAPTURA."""
    from datetime import datetime
    _exec("""INSERT INTO contenedores
        (consecutivo, aduana, anio, folio, contenedor, cliente, estatus, creado, creado_por, activo)
        VALUES (?,?,?,?,?,?,?,?,?,1)""",
        (consecutivo, aduana, anio, folio, contenedor_limpio, cliente,
         "CAPTURA", datetime.now().isoformat(), actor))
    # Historial
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('contenedores',0,?,?,?,?,?)""",
          (actor, "alta", "", f"{consecutivo} {contenedor_limpio}", datetime.now().isoformat()))
    return consecutivo

def listar_contenedores(aduana, limite=None, offset=0, incluir_eliminados=False):
    if incluir_eliminados:
        sql = "SELECT * FROM contenedores WHERE aduana=? ORDER BY id ASC"
    else:
        sql = "SELECT * FROM contenedores WHERE aduana=? AND activo=1 ORDER BY id ASC"
    params = [aduana]
    if limite is not None:
        sql += " LIMIT ? OFFSET ?"
        params += [limite, offset]
    filas, _ = _exec(sql, tuple(params))
    return filas

def contar_contenedores(aduana, incluir_eliminados=False):
    if incluir_eliminados:
        filas, _ = _exec("SELECT COUNT(*) AS n FROM contenedores WHERE aduana=?", (aduana,))
    else:
        filas, _ = _exec("SELECT COUNT(*) AS n FROM contenedores WHERE aduana=? AND activo=1", (aduana,))
    return filas[0]["n"] if filas else 0

def actualizar_campo_contenedor(cid, campo, valor_nuevo, actor):
    """Actualiza un campo y registra en historial."""
    from datetime import datetime
    prev, _ = _exec(f"SELECT {campo} AS v FROM contenedores WHERE id=?", (cid,))
    valor_anterior = prev[0]["v"] if prev else ""
    _exec(f"UPDATE contenedores SET {campo}=? WHERE id=?", (valor_nuevo, cid))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('contenedores',?,?,?,?,?,?)""",
          (cid, actor, campo, str(valor_anterior or ""), str(valor_nuevo), datetime.now().isoformat()))


# ============================================================
# BÚSQUEDA
# ============================================================
def buscar_por_contenedor(contenedor_limpio):
    """Trae TODOS los registros de ese contenedor (puede estar en varias aduanas)."""
    filas, _ = _exec(
        "SELECT * FROM contenedores WHERE contenedor=? AND activo=1 ORDER BY aduana, id DESC",
        (contenedor_limpio,))
    return filas

def buscar_por_cliente(cliente_texto, aduana=None, estatus=None):
    """Trae todos los contenedores de un cliente, con filtros opcionales."""
    sql = "SELECT * FROM contenedores WHERE activo=1 AND cliente LIKE ?"
    params = [f"%{cliente_texto}%"]
    if aduana:
        sql += " AND aduana=?"; params.append(aduana)
    if estatus:
        sql += " AND estatus=?"; params.append(estatus)
    sql += " ORDER BY aduana, id DESC"
    filas, _ = _exec(sql, tuple(params))
    return filas

def eliminar_contenedor(cid, actor, motivo=""):
    """Baja lógica con motivo. Sigue visible solo para admin."""
    from datetime import datetime
    _exec("UPDATE contenedores SET activo=0, motivo_baja=? WHERE id=?", (motivo, cid))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('contenedores',?,?,?,?,?,?)""",
          (cid, actor, "eliminado", "activo", motivo or "(sin motivo)", datetime.now().isoformat()))

def restaurar_contenedor(cid, actor):
    """Deshace una eliminación: vuelve a verse para todos."""
    from datetime import datetime
    _exec("UPDATE contenedores SET activo=1, motivo_baja=NULL WHERE id=?", (cid,))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('contenedores',?,?,?,?,?,?)""",
          (cid, actor, "restaurado", "eliminado", "activo", datetime.now().isoformat()))


# ============================================================
# CATÁLOGOS (vienen de la hoja BASE, editables por admin)
# ============================================================
def inicializar_catalogos():
    _exec("""CREATE TABLE IF NOT EXISTS catalogos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        valor TEXT NOT NULL,
        activo INTEGER DEFAULT 1)""")

def cargar_catalogos_iniciales(catalogos_dict):
    """Carga los catálogos desde el diccionario de la hoja BASE, solo si están vacíos."""
    filas, _ = _exec("SELECT COUNT(*) AS n FROM catalogos")
    if filas and filas[0]["n"] > 0:
        return  # ya cargados, no duplicar
    for tipo, valores in catalogos_dict.items():
        for v in valores:
            _exec("INSERT INTO catalogos (tipo, valor, activo) VALUES (?,?,1)", (tipo, v))

def listar_catalogo(tipo):
    filas, _ = _exec(
        "SELECT valor FROM catalogos WHERE tipo=? AND activo=1 ORDER BY valor", (tipo,))
    return [f["valor"] for f in filas]

def tipos_catalogo():
    filas, _ = _exec("SELECT DISTINCT tipo FROM catalogos WHERE activo=1 ORDER BY tipo")
    return [f["tipo"] for f in filas]

def agregar_valor_catalogo(tipo, valor, actor):
    from datetime import datetime
    valor = valor.strip().upper()
    existe, _ = _exec("SELECT id FROM catalogos WHERE tipo=? AND valor=?", (tipo, valor))
    if existe:
        return False, "Ese valor ya existe en el catálogo."
    _exec("INSERT INTO catalogos (tipo, valor, activo) VALUES (?,?,1)", (tipo, valor))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('catalogos',0,?,?,?,?,?)""",
          (actor, tipo, "", valor, datetime.now().isoformat()))
    return True, f"Agregado a {tipo}: {valor}"

def crear_tipo_catalogo(nuevo_tipo, actor):
    """Crea un nuevo catálogo (columna nueva) con un valor inicial vacío de control."""
    nuevo_tipo = nuevo_tipo.strip().upper()
    existe, _ = _exec("SELECT id FROM catalogos WHERE tipo=? LIMIT 1", (nuevo_tipo,))
    if existe:
        return False, "Ese catálogo ya existe."
    # marcador para que el tipo exista aunque no tenga valores aún
    _exec("INSERT INTO catalogos (tipo, valor, activo) VALUES (?,'(vacío)',0)", (nuevo_tipo,))
    return True, f"Catálogo creado: {nuevo_tipo}"


def limpiar_duplicados_catalogo():
    """Elimina valores repetidos en catalogos, deja solo unicos (un solo UPDATE)."""
    filas, _ = _exec("SELECT id, tipo, valor FROM catalogos WHERE activo=1 ORDER BY tipo, id")
    vistos = set()
    ids_borrar = []
    for f in filas:
        clave = (str(f["tipo"]), str(f["valor"]))
        if clave in vistos:
            ids_borrar.append(int(f["id"]))
        else:
            vistos.add(clave)
    for cid in ids_borrar:
        _exec("UPDATE catalogos SET activo=0 WHERE id=?", (cid,))


def buscar_pedimento_duplicado(aa, pedimento):
    """Busca si ya existe mismo agente aduanal + pedimento. Devuelve fila o None."""
    if not aa or not pedimento:
        return None
    filas, _ = _exec(
        "SELECT * FROM contenedores WHERE aa=? AND pedimento=? AND activo=1 LIMIT 1",
        (aa, pedimento))
    return filas[0] if filas else None

def crear_contenedor_forzado(aduana, contenedor_limpio, cliente, consecutivo, anio, folio, actor, motivo):
    """Alta forzada por admin pese a duplicado. Registra el motivo."""
    from datetime import datetime
    _exec("""INSERT INTO contenedores
        (consecutivo, aduana, anio, folio, contenedor, cliente, estatus, creado, creado_por, activo)
        VALUES (?,?,?,?,?,?,?,?,?,1)""",
        (consecutivo, aduana, anio, folio, contenedor_limpio, cliente,
         "CAPTURA", datetime.now().isoformat(), actor))
    _exec("""INSERT INTO historial (tabla, registro_id, usuario, campo, valor_anterior, valor_nuevo, fecha)
             VALUES ('contenedores',0,?,?,?,?,?)""",
          (actor, "alta forzada", motivo, f"{consecutivo} {contenedor_limpio}", datetime.now().isoformat()))
    return consecutivo


def cargar_pantaco_2026(registros, actor):
    """Carga masiva de los registros 2026 de Pantaco. Una sola vez."""
    from datetime import datetime
    ya, _ = _exec("SELECT COUNT(*) AS n FROM contenedores WHERE aduana='PANTACO'")
    if ya and ya[0]["n"] > 5:
        return 0  # ya hay datos, no recargar
    n = 0
    anio = 2026
    for reg in registros:
        folio = ultimo_folio("PANTACO", anio) + 1
        consec = f"PN-{str(anio)[-2:]}{folio:04d}"
        _exec("""INSERT INTO contenedores
            (consecutivo, aduana, anio, folio, contenedor, aa, referencia, pedimento,
             fecha_pago, cliente, eta, estatus, modulo_t3, importador, detalle, regimen,
             observaciones, creado, creado_por, activo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
            (consec, "PANTACO", anio, folio, reg["contenedor"], reg["aa"], reg["referencia"],
             reg["pedimento"], reg["fecha_pago"], reg["cliente"], reg["eta"],
             reg["estatus"], reg["modulo_t3"], reg["importador"],
             reg["detalle"], reg["regimen"], reg["observaciones"],
             datetime.now().isoformat(), actor))
        n += 1
    return n


def estatus_existentes(aduana=None):
    """Lista de estatus que existen en los datos. '(vacío)' SIEMPRE disponible para supervisar."""
    if aduana:
        filas, _ = _exec("SELECT DISTINCT estatus FROM contenedores WHERE aduana=? AND activo=1 ORDER BY estatus", (aduana,))
    else:
        filas, _ = _exec("SELECT DISTINCT estatus FROM contenedores WHERE activo=1 ORDER BY estatus")
    res = []
    hay_vacio = False
    for f in filas:
        e = f.get("estatus")
        if e and e.strip():
            res.append(e)
        else:
            hay_vacio = True
    # "(vacío)" siempre como opción al inicio, para poder supervisar pendientes sin estatus
    return ["(vacío)"] + res


def buscar_por_estatus(estatus_lista, aduana=None):
    """Trae contenedores cuyo estatus esté en la lista. '' representa vacíos.
    Ordena por ETA (más viejo arriba)."""
    if isinstance(estatus_lista, str):
        estatus_lista = [estatus_lista]
    incluye_vacio = "" in estatus_lista
    con_valor = [e for e in estatus_lista if e != ""]

    condiciones = []
    params = []
    if con_valor:
        placeholders = ",".join("?" for _ in con_valor)
        condiciones.append(f"estatus IN ({placeholders})")
        params.extend(con_valor)
    if incluye_vacio:
        condiciones.append("(estatus IS NULL OR estatus='')")
    if not condiciones:
        return []
    sql = "SELECT * FROM contenedores WHERE activo=1 AND (" + " OR ".join(condiciones) + ")"
    if aduana:
        sql += " AND aduana=?"; params.append(aduana)
    filas, _ = _exec(sql, tuple(params))
    return _ordenar_por_eta(filas)

def _ordenar_por_eta(filas):
    """Ordena por ETA dd/mm/yyyy, más viejo primero. Vacíos al final."""
    from datetime import datetime
    def clave(f):
        eta = f.get("eta") or ""
        try:
            return (0, datetime.strptime(eta.strip(), "%d/%m/%Y"))
        except Exception:
            return (1, datetime.max)
    return sorted(filas, key=clave)


def corregir_estatus_vacios_2026(registros):
    """Corrige los registros 2026 que se cargaron como CAPTURA pero debían ir vacíos."""
    n = 0
    for reg in registros:
        if not reg["estatus"].strip():  # debía ir vacío
            # buscar ese contenedor con estatus CAPTURA y vaciarlo
            filas, _ = _exec(
                "SELECT id FROM contenedores WHERE contenedor=? AND aduana='PANTACO' AND estatus='CAPTURA'",
                (reg["contenedor"],))
            for f in filas:
                _exec("UPDATE contenedores SET estatus='' WHERE id=?", (f["id"],))
                n += 1
    return n
