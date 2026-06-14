"""
RUCO - Interfaz (la cara que la gente usa).
Esta pieza es solo presentación. Toda la lógica vive en core/.
"""
import streamlit as st
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from core import datos, reglas

st.set_page_config(page_title="RUCO", page_icon="📦", layout="wide")

datos.inicializar()
datos.inicializar_catalogos()
# Cargar catálogos de la hoja BASE la primera vez
import json as _json, os as _os2
_ruta_cat = _os2.path.join(_os2.path.dirname(__file__), "catalogos_base.json")
if _os2.path.exists(_ruta_cat):
    with open(_ruta_cat, encoding="utf-8") as _fc:
        datos.cargar_catalogos_iniciales(_json.load(_fc))
try:
    datos.limpiar_duplicados_catalogo()
except Exception:
    pass


# ---------- Estilo visual ----------
st.markdown("""
<style>
:root {
  --negro: #000000;
  --gris-panel: #1a1a1a;
  --gris-sel: #2a2a2a;
  --ambar: #E8A33D;
  --texto: #FFFFFF;
  --texto-sec: #9aa0a6;
}
/* Ocultar barra y menu de Streamlit */
#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
footer {visibility: hidden;}
.stAppDeployButton {display: none;}
.stApp { background: #000000; color: #FFFFFF; }
/* Texto general en blanco */
.stApp, .stApp p, .stApp label, .stApp span, .stApp div,
h1,h2,h3,h4,h5,h6 { color: #FFFFFF; }
/* Encabezado RUCO */
.ruco-header {
  background: linear-gradient(100deg, #111111, #1a1a1a);
  padding: 1.1rem 1.5rem; border-radius: 12px; margin-bottom: 1.2rem;
  display:flex; align-items:center; justify-content:space-between;
  border: 1px solid #2a2a2a;
}
.ruco-title { color:#FFFFFF; font-size:1.5rem; font-weight:800; letter-spacing:-0.5px; margin:0; }
.ruco-sub { color:#9aa0a6; font-size:0.78rem; margin:0; letter-spacing:2px; }
.ruco-user { color:#E8A33D; font-weight:700; font-size:0.9rem; }
/* Campos de texto: fondo gris oscuro, texto blanco */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  background-color: #1a1a1a !important;
  color: #FFFFFF !important;
  border: 1px solid #333 !important;
}
/* Selecciones / hover en gris */
.stSelectbox div[data-baseweb="select"]:hover > div,
li:hover, [role="option"]:hover { background-color: #2a2a2a !important; }
/* Botón primario verde tenue */
div.stButton > button[kind="primary"] {
  background: #3f9d6b; color:#FFFFFF; border:none; font-weight:700;
}
div.stButton > button[kind="primary"]:hover { background:#4caf7d; }
/* Botones secundarios oscuros */
div.stButton > button { background:#1a1a1a; color:#FFFFFF; border:1px solid #333; }
/* Botón del contenedor: texto grande y prominente */
.lista-cont div.stButton > button { font-size:1.1rem; font-weight:800; letter-spacing:0.5px; }
/* Cesto eliminar: naranja tenue (botones con clase ruco-del) */
.ruco-del-marker + div div.stButton > button,
div.stButton > button:has(span.ruco-trash) {
  background:#b07a4a !important; border-color:#c98a55 !important; color:#fff !important;
}
div.stButton > button:hover { background:#2a2a2a; border-color:#555; }
/* Contenedores con borde */
[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
  background:#0d0d0d; border-color:#2a2a2a !important;
}
/* Pestañas */
.stTabs [data-baseweb="tab"] { color:#9aa0a6; }
.stTabs [aria-selected="true"] { color:#E8A33D !important; }
.badge-on { color:#3ddc84; font-weight:700; }
.badge-off { color:#ff6b6b; font-weight:700; }
/* Suavizar el oscurecido que aparece mientras la app recarga */
[data-testid="stStatusWidget"] { display:none; }
div[data-stale="true"], .stApp [data-stale="true"] {
  opacity: 1 !important;
  transition: opacity 0.15s ease;
}
[data-testid="stAppViewBlockContainer"], .element-container { opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# ---------- Estado de sesión ----------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ---------- LOGIN ----------
def pantalla_login():
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:1.5rem'>
          <div style='font-size:2.6rem; font-weight:800; color:#FFFFFF; letter-spacing:-1px'>RUCO</div>
          <div style='color:#9aa0a6; font-size:0.8rem; letter-spacing:3px'>REPORTE ÚNICO DE CONTENEDORES OFICIAL</div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Entrar", type="primary", use_container_width=True):
                u = datos.autenticar(usuario, password)
                if u:
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos, o cuenta desactivada.")

# ---------- HEADER ----------
def header():
    u = st.session_state.usuario
    st.markdown(f"""
    <div class='ruco-header'>
      <div>
        <p class='ruco-title'>RUCO</p>
        <p class='ruco-sub'>REPORTE ÚNICO DE CONTENEDORES OFICIAL</p>
      </div>
      <div style='text-align:right'>
        <div class='ruco-user'>{u['nombre']}</div>
        <div style='color:#A9C0E0; font-size:0.75rem'>{u['rol']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- PANEL ADMIN: USUARIOS ----------
def panel_usuarios():
    st.subheader("Gestión de usuarios")
    actor = st.session_state.usuario["usuario"]
    mi_rol = st.session_state.usuario["rol"]

    with st.expander("➕ Crear nuevo usuario", expanded=False):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre completo")
        usuario = c2.text_input("Usuario (para entrar)")
        c3, c4 = st.columns(2)
        password = c3.text_input("Contraseña inicial", type="password")
        # Roles que puede asignar según quién es (admin ve Supervisión; supervisión solo operativos)
        opciones_rol = datos.roles_asignables(mi_rol)
        rol = c4.selectbox("Área / Rol", opciones_rol)
        cliente = ""
        if rol == "Consulta cliente":
            cliente = st.text_input("Cliente ligado (solo verá lo de este cliente)")
        # Casilla extra: solo el admin puede dar permiso de gestionar usuarios, y solo a Supervisión
        permite_gestion = False
        if mi_rol == "Administrador" and rol == "Supervisión":
            permite_gestion = st.checkbox(
                "Permitir que este supervisor cree usuarios operativos",
                help="Si lo activas, podrá crear usuarios operativos (nunca administradores ni supervisores).")
        if st.button("Crear usuario", type="primary"):
            if not (nombre and usuario and password):
                st.warning("Llena nombre, usuario y contraseña.")
            elif rol == "Consulta cliente" and not cliente:
                st.warning("Un usuario de consulta cliente necesita el cliente ligado.")
            else:
                ok, msg = datos.crear_usuario(nombre, usuario, password, rol, cliente, actor)
                if ok:
                    # Si es supervisión con gestión, guardar ese permiso
                    if permite_gestion:
                        nuevo = datos.obtener_usuario_por_username(usuario.strip().lower())
                        if nuevo:
                            datos.guardar_permisos(nuevo["id"], ["gestionar_usuarios"], actor)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("##### Usuarios registrados")
    soy_admin = mi_rol == "Administrador"
    for u in datos.listar_usuarios():
        c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1.3, 1, 1])
        estado = "<span class='badge-on'>● Activo</span>" if u["activo"] else "<span class='badge-off'>○ Inactivo</span>"
        ligado = f" · cliente: {u['cliente_ligado']}" if u["cliente_ligado"] else ""
        # Nombre clicable -> abre perfil de permisos (solo el admin puede)
        if soy_admin:
            if c1.button(f"{u['nombre']}  ·  {u['usuario']}", key=f"perfil_{u['id']}"):
                st.session_state[f"abriendo_perfil_{u['id']}"] = not st.session_state.get(f"abriendo_perfil_{u['id']}", False)
        else:
            c1.markdown(f"**{u['nombre']}**  \n`{u['usuario']}`")
        c2.markdown(f"{u['rol']}{ligado}")
        c3.markdown(estado, unsafe_allow_html=True)
        # Solo el admin edita/elimina usuarios. Supervisión solo crea.
        es_protegido = (u["rol"] == "Administrador" and u["usuario"] == "admin") or u["usuario"] == "consulta"
        if soy_admin and not es_protegido:
            if u["activo"]:
                if c4.button("Desactivar", key=f"off{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], False, actor); st.rerun()
            else:
                if c4.button("Activar", key=f"on{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], True, actor); st.rerun()
            if c5.button("Eliminar", key=f"delu{u['id']}"):
                st.session_state[f"borrar_user_{u['id']}"] = True
            if st.session_state.get(f"borrar_user_{u['id']}"):
                st.warning(f"¿Eliminar a **{u['nombre']}** ({u['usuario']})? No se puede deshacer.")
                bc = st.columns(2)
                if bc[0].button("Sí, eliminar", type="primary", key=f"delu_si{u['id']}"):
                    datos.eliminar_usuario(u["id"], actor)
                    st.session_state[f"borrar_user_{u['id']}"] = False
                    st.rerun()
                if bc[1].button("Cancelar", key=f"delu_no{u['id']}"):
                    st.session_state[f"borrar_user_{u['id']}"] = False
                    st.rerun()

        # Perfil de permisos (solo el admin lo ve)
        if soy_admin and st.session_state.get(f"abriendo_perfil_{u['id']}"):
            with st.container(border=True):
                if es_protegido:
                    if u["usuario"] == "consulta":
                        st.info("Usuario de SOLO CONSULTA. Ve todo y busca, pero no modifica nada. Fijo del sistema.")
                    else:
                        st.info("El administrador puede editar todo. No requiere permisos.")
                else:
                    # Editar datos del usuario (nombre, usuario, contraseña, rol)
                    st.markdown(f"**Datos de {u['nombre']}**")
                    ec1, ec2 = st.columns(2)
                    ed_nombre = ec1.text_input("Nombre completo", value=u["nombre"], key=f"edu_nom_{u['id']}")
                    ed_usuario = ec2.text_input("Usuario (para entrar)", value=u["usuario"], key=f"edu_usr_{u['id']}")
                    ec3, ec4 = st.columns(2)
                    ed_pass = ec3.text_input("Nueva contraseña (dejar vacío = sin cambio)",
                                             type="password", key=f"edu_pwd_{u['id']}")
                    roles_op = datos.roles_asignables("Administrador")
                    rol_idx = roles_op.index(u["rol"]) if u["rol"] in roles_op else 0
                    ed_rol = ec4.selectbox("Área / Rol", roles_op, index=rol_idx, key=f"edu_rol_{u['id']}")
                    ed_cliente = u.get("cliente_ligado") or ""
                    if ed_rol == "Consulta cliente":
                        ed_cliente = st.text_input("Cliente ligado", value=ed_cliente, key=f"edu_cli_{u['id']}")
                    # Mostrar confirmación persistente si la hubo
                    if st.session_state.get(f"msg_usuario_{u['id']}"):
                        st.success(st.session_state[f"msg_usuario_{u['id']}"])
                        del st.session_state[f"msg_usuario_{u['id']}"]

                    if st.button("Guardar datos del usuario", type="primary", key=f"edu_save_{u['id']}"):
                        ok, msg = datos.editar_usuario(
                            u["id"], ed_nombre, ed_usuario, ed_rol, ed_cliente, actor,
                            password=ed_pass if ed_pass else None)
                        if ok:
                            cambios = "✅ Cambios guardados"
                            if ed_pass:
                                cambios += " (contraseña actualizada)"
                            st.session_state[f"msg_usuario_{u['id']}"] = cambios + "."
                            st.rerun()
                        else:
                            st.error(msg)

                    st.divider()
                    st.markdown(f"**Permisos de edición de {u['nombre']}**")
                    st.caption("Marca los campos que este usuario PUEDE editar. Los demás solo los verá.")
                    if st.session_state.get(f"msg_perm_{u['id']}"):
                        st.success(st.session_state[f"msg_perm_{u['id']}"])
                        del st.session_state[f"msg_perm_{u['id']}"]
                    permisos_actuales = datos.obtener_permisos(u["id"])
                    estatus_actuales = datos.obtener_estatus_permitidos(u["id"])
                    seleccion = []
                    # casillas en 3 columnas
                    campos = datos.CAMPOS_EDITABLES
                    colp = st.columns(3)
                    marco_estatus = False
                    for i, (clave, etiqueta) in enumerate(campos):
                        with colp[i % 3]:
                            marcado = st.checkbox(etiqueta, value=(clave in permisos_actuales),
                                                  key=f"perm_{u['id']}_{clave}")
                            if marcado:
                                seleccion.append(clave)
                                if clave == "estatus":
                                    marco_estatus = True
                    # Si marcó ESTATUS, mostrar cuáles estatus puede poner
                    estatus_sel = []
                    if marco_estatus:
                        st.markdown("**¿Qué estatus puede poner este usuario?**")
                        st.caption("Marca solo los que tiene permitido asignar. Al menos uno.")
                        cols_e = st.columns(4)
                        for j, est in enumerate(reglas.ESTATUS):
                            with cols_e[j % 4]:
                                if st.checkbox(est, value=(est in estatus_actuales),
                                               key=f"est_{u['id']}_{est}"):
                                    estatus_sel.append(est)
                    if st.button("Guardar permisos", type="primary", key=f"savperm_{u['id']}"):
                        # Validar: si tiene permiso de estatus, debe marcar al menos uno
                        if marco_estatus and not estatus_sel:
                            st.error("Diste permiso de Estatus. Marca al menos un estatus que pueda poner.")
                        else:
                            if "gestionar_usuarios" in permisos_actuales:
                                seleccion.append("gestionar_usuarios")
                            datos.guardar_permisos(u["id"], seleccion, actor)
                            # guardar estatus permitidos (vacío si no marcó estatus)
                            datos.guardar_estatus_permitidos(u["id"], estatus_sel if marco_estatus else [], actor)
                            st.session_state[f"msg_perm_{u['id']}"] = "✅ Permisos guardados."
                            st.rerun()

# ---------- PANEL ADMIN: HISTORIAL ----------
def panel_historial():
    st.subheader("Historial de cambios")
    h = datos.historial_reciente()
    if not h:
        st.info("Aún no hay movimientos registrados.")
        return
    for x in h:
        st.markdown(
            f"<div style='border-left:3px solid #E8A33D; padding:.2rem .8rem; margin:.3rem 0;'>"
            f"<b>{x['usuario']}</b> · {x['tabla']} · {x['campo']}: "
            f"<i>{x['valor_anterior'] or '—'}</i> → <b>{x['valor_nuevo']}</b>"
            f"<br><span style='color:#5B6B7E; font-size:.75rem'>{x['fecha'][:16].replace('T',' ')}</span></div>",
            unsafe_allow_html=True)

# ---------- PANEL: REPORTES ----------
def panel_reportes():
    st.subheader("📊 Reportes")
    st.info("Aquí se generarán los reportes en Excel con el formato fijo de RUCO. "
            "Esta sección se construye la próxima semana.")
    st.caption("Pronto podrás filtrar por aduana, cliente, estatus y fechas, y descargar el reporte en Excel "
               "respetando las columnas de tu hoja original.")

# ---------- PANEL ADUANA: PANTACO ----------
datos.inicializar_contenedores()

def _campo_fecha(label, valor, key):
    """Campo de fecha con formato dd/mm/yyyy guiado."""
    return st.text_input(label, value=valor or "", key=key,
                         placeholder="dd/mm/yyyy", max_chars=10)


def _ficha_edicion(ct, actor, es_admin):
    st.markdown(f"#### Editar {ct['contenedor']}")

    # Determinar qué campos puede editar este usuario
    if es_admin:
        permitidos = [c[0] for c in datos.CAMPOS_EDITABLES]  # admin edita todo
        estatus_permitidos = reglas.ESTATUS  # admin pone cualquiera
    else:
        usr = datos.obtener_usuario_por_username(actor)
        permitidos = datos.obtener_permisos(usr["id"]) if usr else []
        estatus_permitidos = datos.obtener_estatus_permitidos(usr["id"]) if usr else []

    def puede(campo):
        return campo in permitidos

    def mostrar_solo_lectura(etiqueta, valor):
        st.markdown(
            f"<div style='font-size:0.72rem;color:#9aa0a6'>{etiqueta}</div>"
            f"<div style='padding:6px 0;color:#cfcfcf'>{valor or '—'}</div>",
            unsafe_allow_html=True)

    cli = datos.listar_catalogo("CLIENTE")
    imp = datos.listar_catalogo("IMPORTADOR")
    aas = datos.listar_catalogo("AA")
    regs = datos.listar_catalogo("REGIMEN")
    dets = datos.listar_catalogo("DETALLE")
    t3s = datos.listar_catalogo("T3")
    ests = estatus_permitidos  # solo los que este usuario puede poner

    def opciones_con_actual(catalogo, valor_actual):
        """Lista que arranca con el valor actual del contenedor ya seleccionado."""
        va = (valor_actual or "").strip()
        if va and va in catalogo:
            # poner el actual primero
            return [va] + [x for x in catalogo if x != va]
        elif va:
            # valor actual no está en catálogo (raro), lo agregamos arriba
            return [va] + catalogo
        else:
            return ["(vacío)"] + catalogo

    n_cli = n_imp = n_aa = n_ref = n_ped = n_eta = "(sin cambio)"
    n_reg = n_det = n_fp = n_t3 = n_obs = n_est = "(sin cambio)"

    # Fila 1: cliente, importador, agente
    r1 = st.columns(3)
    with r1[0]:
        if puede("cliente"): n_cli = st.selectbox("CLIENTE", opciones_con_actual(cli, ct.get("cliente")), key=f"ed_cli_{ct['id']}")
        else: mostrar_solo_lectura("CLIENTE", ct.get("cliente"))
    with r1[1]:
        if puede("importador"): n_imp = st.selectbox("IMPORTADOR", opciones_con_actual(imp, ct.get("importador")), key=f"ed_imp_{ct['id']}")
        else: mostrar_solo_lectura("IMPORTADOR", ct.get("importador"))
    with r1[2]:
        if puede("aa"): n_aa = st.selectbox("AGENTE ADUANAL", opciones_con_actual(aas, ct.get("aa")), key=f"ed_aa_{ct['id']}")
        else: mostrar_solo_lectura("AGENTE ADUANAL", ct.get("aa"))
    # Fila 2: referencia, pedimento, ETA
    r2 = st.columns(3)
    with r2[0]:
        if puede("referencia"): n_ref = st.text_input("REFERENCIA", value=ct.get("referencia") or "", key=f"ed_ref_{ct['id']}")
        else: mostrar_solo_lectura("REFERENCIA", ct.get("referencia"))
    with r2[1]:
        if puede("pedimento"): n_ped = st.text_input("PEDIMENTO", value=ct.get("pedimento") or "", key=f"ed_ped_{ct['id']}")
        else: mostrar_solo_lectura("PEDIMENTO", ct.get("pedimento"))
    with r2[2]:
        if puede("eta"): n_eta = st.text_input("ETA", value=ct.get("eta") or "", placeholder="dd/mm/yyyy", max_chars=10, key=f"ed_eta_{ct['id']}")
        else: mostrar_solo_lectura("ETA", ct.get("eta"))
    # Fila 3: regimen, detalle, fecha pago
    r3 = st.columns(3)
    with r3[0]:
        if puede("regimen"): n_reg = st.selectbox("REGIMEN", opciones_con_actual(regs, ct.get("regimen")), key=f"ed_reg_{ct['id']}")
        else: mostrar_solo_lectura("REGIMEN", ct.get("regimen"))
    with r3[1]:
        if puede("detalle"): n_det = st.selectbox("DETALLE", opciones_con_actual(dets, ct.get("detalle")), key=f"ed_det_{ct['id']}")
        else: mostrar_solo_lectura("DETALLE", ct.get("detalle"))
    with r3[2]:
        if puede("estatus"): n_est = st.selectbox("ESTATUS", opciones_con_actual(ests, ct.get("estatus")), key=f"ed_est_{ct['id']}")
        else: mostrar_solo_lectura("ESTATUS", ct.get("estatus") or "SIN ESTATUS")
    # Fila 4: módulo T3 (focos), fecha de pago
    r4 = st.columns(3)
    with r4[0]:
        # MÓDULO T3 como semáforo de focos. Guarda texto: VERDE / ROJO / BLOQUEADO
        T3_OPCIONES = ["🟢 VERDE", "🔴 ROJO", "🔵 BLOQUEADO"]
        T3_MAP = {"🟢 VERDE": "VERDE", "🔴 ROJO": "ROJO", "🔵 BLOQUEADO": "BLOQUEADO"}
        T3_INV = {"VERDE": "🟢 VERDE", "ROJO": "🔴 ROJO", "BLOQUEADO": "🔵 BLOQUEADO"}
        actual_t3 = (ct.get("modulo_t3") or "").strip().upper()
        ya_tiene_t3 = actual_t3 in T3_INV
        # El ejecutivo puede ponerlo solo si está vacío. Si ya tiene, solo el admin lo cambia.
        puede_editar_t3 = es_admin or (puede("modulo_t3") and not ya_tiene_t3)
        if puede_editar_t3:
            idx_t3 = T3_OPCIONES.index(T3_INV[actual_t3]) if ya_tiene_t3 else 0
            sel_t3 = st.radio("MODULO T3", T3_OPCIONES, index=idx_t3, horizontal=False, key=f"ed_t3_{ct['id']}")
            n_t3 = T3_MAP[sel_t3]
        else:
            # Solo lectura (ya tiene foco y no es admin, o no tiene permiso)
            mostrar_solo_lectura("MODULO T3", T3_INV.get(actual_t3, "—"))
            if puede("modulo_t3") and ya_tiene_t3 and not es_admin:
                st.caption("Ya asignado. Solo el administrador puede cambiarlo.")
            n_t3 = "(sin cambio)"
    with r4[1]:
        if puede("fecha_pago"): n_fp = st.text_input("FECHA DE PAGO", value=ct.get("fecha_pago") or "", placeholder="dd/mm/yyyy", max_chars=10, key=f"ed_fp_{ct['id']}")
        else: mostrar_solo_lectura("FECHA DE PAGO", ct.get("fecha_pago"))
    # Observaciones acumulativas (historial con autor, no se borra)
    obs_historial = ct.get("observaciones") or ""
    st.markdown("<div style='font-size:0.72rem;color:#9aa0a6;margin-top:8px'>OBSERVACIONES</div>", unsafe_allow_html=True)
    n_obs = ""
    obs_admin_edit = None
    if es_admin:
        # El admin ve y edita TODO el historial como campo de texto (puede borrar/modificar)
        obs_admin_edit = st.text_area(
            "Historial de observaciones (editable solo para ti)",
            value=obs_historial,
            height=160,
            key=f"ed_obs_admin_{ct['id']}")
        st.caption("Puedes corregir o borrar cualquier observación. Para agregar una nueva con tu nombre y fecha, usa el campo de abajo.")
        n_obs = st.text_input("AGREGAR NUEVA OBSERVACIÓN",
                              value="", placeholder="Escribe aquí la nueva observación...",
                              key=f"ed_obs_nueva_{ct['id']}")
    else:
        # Los demás ven el historial completo (con nombres y fechas) pero no lo editan
        if obs_historial.strip():
            st.markdown(
                "<div style='background:#1a1d23;border:1px solid #2a2e35;border-radius:8px;"
                "padding:10px;white-space:pre-wrap;color:#cfcfcf;font-size:0.85rem;max-height:220px;overflow-y:auto'>"
                f"{obs_historial}</div>", unsafe_allow_html=True)
        else:
            st.caption("Sin observaciones todavía.")
        if puede("observaciones"):
            n_obs = st.text_area("AGREGAR NUEVA OBSERVACIÓN",
                                 value="", placeholder="Escribe aquí la nueva observación...",
                                 key=f"ed_obs_{ct['id']}")

    # Si no puede editar NADA, avisar
    if not permitidos and not es_admin:
        st.info("Solo puedes consultar este contenedor. No tienes campos asignados para editar.")

    if (permitidos or es_admin) and st.button("Guardar cambios", type="primary", key=f"ed_save_{ct['id']}"):
        eta_val = n_eta if (n_eta and n_eta != "(sin cambio)") else ""
        fp_val = n_fp if (n_fp and n_fp != "(sin cambio)") else ""
        ok_eta, msg_eta = reglas.validar_fecha(eta_val)
        ok_fp, msg_fp = reglas.validar_fecha(fp_val)
        if puede("eta") and not ok_eta:
            st.error(f"ETA: {msg_eta}"); return
        if puede("fecha_pago") and not ok_fp:
            st.error(f"FECHA DE PAGO: {msg_fp}"); return
        if puede("referencia") and n_ref.strip():
            okr, vr = reglas.validar_referencia(n_ref)
            if not okr: st.error(f"REFERENCIA: {vr}"); return
            datos.actualizar_campo_contenedor(ct["id"], "referencia", vr, actor)
        if puede("pedimento") and n_ped.strip():
            okp, vp = reglas.validar_pedimento(n_ped)
            if not okp: st.error(f"PEDIMENTO: {vp}"); return
            datos.actualizar_campo_contenedor(ct["id"], "pedimento", vp, actor)
        for campo, val in [("cliente",n_cli),("importador",n_imp),("aa",n_aa),
                           ("regimen",n_reg),("detalle",n_det),("estatus",n_est)]:
            if puede(campo) and val and val not in ("(sin cambio)", "(vacío)"):
                nuevo_val = reglas.normalizar_texto(val)
                if nuevo_val != (ct.get(campo) or "").strip():
                    datos.actualizar_campo_contenedor(ct["id"], campo, nuevo_val, actor)
        # MÓDULO T3 (focos): puede quedar vacío "Sin definir", se guarda tal cual
        if puede("modulo_t3") and n_t3 != "(sin cambio)":
            if n_t3 != (ct.get("modulo_t3") or "").strip():
                datos.actualizar_campo_contenedor(ct["id"], "modulo_t3", n_t3, actor)
        if puede("eta") and n_eta != "(sin cambio)" and n_eta.strip() != (ct.get("eta") or "").strip():
            datos.actualizar_campo_contenedor(ct["id"], "eta", n_eta.strip(), actor)
        if puede("fecha_pago") and n_fp != "(sin cambio)" and n_fp.strip() != (ct.get("fecha_pago") or "").strip():
            datos.actualizar_campo_contenedor(ct["id"], "fecha_pago", n_fp.strip(), actor)
        # OBSERVACIONES
        if es_admin:
            # 1) Si el admin editó el historial completo, guardar esa versión
            base_obs = obs_admin_edit if obs_admin_edit is not None else (ct.get("observaciones") or "")
            if base_obs != (ct.get("observaciones") or ""):
                datos.actualizar_campo_contenedor(ct["id"], "observaciones", base_obs, actor)
            # 2) Si además escribió una nueva, anexarla con nombre y fecha
            if n_obs.strip():
                usr_actual = datos.obtener_usuario_por_username(actor)
                nombre_perfil = usr_actual["nombre"] if usr_actual else actor
                sello = datetime.now().strftime("%d/%m/%Y %H:%M")
                nueva_obs = f"{nombre_perfil} - {reglas.normalizar_texto(n_obs)} - {sello}"
                base_obs = base_obs.strip()
                obs_final = (base_obs + "\n-----\n" + nueva_obs) if base_obs else nueva_obs
                datos.actualizar_campo_contenedor(ct["id"], "observaciones", obs_final, actor)
        elif puede("observaciones") and n_obs.strip():
            # Los demás solo anexan (no pueden borrar ni modificar lo anterior)
            usr_actual = datos.obtener_usuario_por_username(actor)
            nombre_perfil = usr_actual["nombre"] if usr_actual else actor
            sello = datetime.now().strftime("%d/%m/%Y %H:%M")
            nueva_obs = f"{nombre_perfil} - {reglas.normalizar_texto(n_obs)} - {sello}"
            historial_prev = (ct.get("observaciones") or "").strip()
            obs_final = (historial_prev + "\n-----\n" + nueva_obs) if historial_prev else nueva_obs
            datos.actualizar_campo_contenedor(ct["id"], "observaciones", obs_final, actor)
        st.session_state[f"msg_guardado_{ct['id']}"] = "✅ Cambios guardados."
        st.session_state[f"editando_{ct['id']}"] = False
        st.rerun()
    if st.button("Cerrar", key=f"ed_close_{ct['id']}"):
        st.session_state[f"editando_{ct['id']}"] = False
        st.rerun()


def _crear_alta(aduana_key, limpio, cliente_norm, aa_final, ref_val, ped_val, actor, clasif, forzado):
    anio = datetime.now().year
    folio = datos.ultimo_folio(aduana_key, anio) + 1
    consec = reglas.generar_consecutivo(aduana_key, anio, folio - 1)
    if forzado:
        datos.crear_contenedor_forzado(aduana_key, limpio, cliente_norm,
            consec, anio, folio, actor, "alta duplicada autorizada por admin")
        st.warning(f"Alta DUPLICADA autorizada: {consec} · {limpio}")
    else:
        datos.crear_contenedor(aduana_key, limpio, cliente_norm, consec, anio, folio, actor)
        if clasif == "REINGRESO":
            st.success(f"Reingreso: {consec} · {limpio} (+3 meses).")
        else:
            st.success(f"Alta: {consec} · {limpio}")
    nuevo = datos.buscar_contenedor_existente(limpio)
    if nuevo:
        if aa_final: datos.actualizar_campo_contenedor(nuevo["id"], "aa", aa_final, actor)
        if ref_val: datos.actualizar_campo_contenedor(nuevo["id"], "referencia", ref_val, actor)
        if ped_val: datos.actualizar_campo_contenedor(nuevo["id"], "pedimento", ped_val, actor)


def panel_aduana(aduana_key, aduana_nombre):
    actor = st.session_state.usuario["usuario"]
    es_admin = st.session_state.usuario["rol"] == "Administrador"
    st.subheader(f"CONTENEDORES · {aduana_nombre.upper()}")

    # Versión del formulario: al subir, todos los widgets nacen vacíos (limpieza total)
    vkey = f"altaver_{aduana_key}"
    if vkey not in st.session_state:
        st.session_state[vkey] = 0
    v = st.session_state[vkey]

    with st.expander("➕ DAR DE ALTA UN CONTENEDOR", expanded=True):
        clientes_cat = datos.listar_catalogo("CLIENTE")
        aas_cat = datos.listar_catalogo("AA")

        # Fila 1: contenedor, cliente (solo selección, nuevos se agregan en Base)
        r1 = st.columns(2)
        cont_raw = r1[0].text_input("NÚMERO DE CONTENEDOR", max_chars=11,
                                    key=f"alta_cont_{aduana_key}_{v}",
                                    help="11 caracteres: 4 letras + 7 dígitos")
        cliente_sel = r1[1].selectbox("CLIENTE", ["(seleccionar)"] + clientes_cat,
                                      key=f"alta_clisel_{aduana_key}_{v}")

        # Fila 2: agente aduanal, referencia, pedimento
        r2 = st.columns(3)
        aa_sel = r2[0].selectbox("AGENTE ADUANAL", ["(opcional)"] + aas_cat, key=f"alta_aa_{aduana_key}_{v}")
        ref_raw = r2[1].text_input("REFERENCIA", key=f"alta_ref_{aduana_key}_{v}")
        ped_raw = r2[2].text_input("PEDIMENTO", key=f"alta_ped_{aduana_key}_{v}")

        if st.button("DAR DE ALTA", type="primary", key=f"alta_btn_{aduana_key}"):
            limpio = reglas.limpiar_contenedor(cont_raw)
            ok, msg = reglas.validar_contenedor(cont_raw)
            cliente_final = "" if cliente_sel == "(seleccionar)" else cliente_sel
            cliente_norm = reglas.normalizar_texto(cliente_final)
            aa_final = "" if aa_sel == "(opcional)" else aa_sel

            if not cliente_norm:
                st.warning("El cliente es obligatorio.")
            elif not ok:
                st.error(f"Contenedor inválido: {msg}")
            else:
                ref_val = ""; ped_val = ""
                err = None
                if ref_raw.strip():
                    okr, ref_val = reglas.validar_referencia(ref_raw)
                    if not okr: err = f"REFERENCIA: {ref_val}"
                if ped_raw.strip() and not err:
                    okp, ped_val = reglas.validar_pedimento(ped_raw)
                    if not okp: err = f"PEDIMENTO: {ped_val}"
                if err:
                    st.error(err)
                else:
                    previo = datos.buscar_contenedor_existente(limpio)
                    clasif = "NUEVO"
                    if previo:
                        m = reglas.meses_entre(previo.get("creado"))
                        clasif = reglas.evaluar_duplicado(m)
                    ped_dup = datos.buscar_pedimento_duplicado(aa_final, ped_val) if ped_val else None
                    hay_dup = clasif == "DUDOSO" or ped_dup is not None

                    avisos = []
                    if clasif == "DUDOSO":
                        avisos.append(f"contenedor ya existe (-3 meses, {previo.get('consecutivo')})")
                    if ped_dup:
                        avisos.append(f"pedimento ya existe con ese agente ({ped_dup.get('consecutivo')})")

                    if hay_dup and not es_admin:
                        st.error("⚠️ DUPLICADO: " + "; ".join(avisos) +
                                 ". No puedes dar de alta. Requiere autorización del administrador.")
                    elif hay_dup and es_admin:
                        # Guardar datos pendientes y pedir confirmación
                        st.session_state[f"dup_pend_{aduana_key}"] = {
                            "limpio": limpio, "cliente": cliente_norm, "aa": aa_final,
                            "ref": ref_val, "ped": ped_val, "avisos": avisos}
                        st.rerun()
                    else:
                        _crear_alta(aduana_key, limpio, cliente_norm, aa_final, ref_val,
                                    ped_val, actor, clasif, forzado=False)
                        st.session_state[vkey] += 1
                        st.rerun()

        # Confirmación de duplicado (solo admin)
        pend = st.session_state.get(f"dup_pend_{aduana_key}")
        if pend:
            st.warning("⚠️ DUPLICADO detectado: " + "; ".join(pend["avisos"]))
            cc = st.columns(2)
            if cc[0].button("Autorizar alta duplicada", type="primary", key=f"dup_si_{aduana_key}"):
                _crear_alta(aduana_key, pend["limpio"], pend["cliente"], pend["aa"],
                            pend["ref"], pend["ped"], actor, "NUEVO", forzado=True)
                del st.session_state[f"dup_pend_{aduana_key}"]
                st.session_state[vkey] += 1
                st.rerun()
            if cc[1].button("Cancelar", key=f"dup_no_{aduana_key}"):
                del st.session_state[f"dup_pend_{aduana_key}"]
                st.rerun()

    # Lista colapsada y paginada (admin ve también eliminados)
    total = datos.contar_contenedores(aduana_key, incluir_eliminados=es_admin)
    with st.expander(f"📋 VER LISTA DE CONTENEDORES ({total})", expanded=False):
        if total == 0:
            st.info("Aún no hay contenedores capturados.")
            return
        POR_PAGINA = 20
        npag = (total - 1) // POR_PAGINA + 1
        pag = st.number_input("Página", min_value=1, max_value=npag, value=1, key=f"pag_{aduana_key}")
        conts = datos.listar_contenedores(aduana_key, limite=POR_PAGINA,
                                          offset=(pag-1)*POR_PAGINA, incluir_eliminados=es_admin)
        for ct in conts:
            eliminado = not ct.get("activo")
            with st.container(border=True):
                if eliminado:
                    # Vista de eliminado (solo admin lo ve), en rojo, con motivo y restaurar
                    cols = st.columns([2, 2.6, 1])
                    cols[0].markdown(
                        f"<span style='color:#ff6b6b'>**{ct['consecutivo']}** (ELIMINADO)  \n"
                        f"`{ct['contenedor']}`</span>", unsafe_allow_html=True)
                    cols[1].markdown(
                        f"<span style='color:#ff9b9b'>CLIENTE: {ct.get('cliente') or '—'}  \n"
                        f"MOTIVO: {ct.get('motivo_baja') or '(sin motivo)'}</span>",
                        unsafe_allow_html=True)
                    if cols[2].button("↩️ Restaurar", key=f"rest_{ct['id']}"):
                        datos.restaurar_contenedor(ct["id"], actor)
                        st.rerun()
                else:
                    cols = st.columns([2.4, 2, 1.4, 0.6]) if es_admin else st.columns([2.4, 2, 1.4])
                    color = reglas.color_estatus(ct.get("estatus"))
                    # Contenedor como botón-link (al darle clic abre/cierra la ficha)
                    if cols[0].button(ct['contenedor'], key=f"open_{ct['id']}",
                                      help="Clic para abrir / editar"):
                        st.session_state[f"editando_{ct['id']}"] = not st.session_state.get(f"editando_{ct['id']}", False)
                    cols[0].markdown(
                        f"<div style='font-size:0.72rem;color:#9aa0a6;margin-top:-8px'>"
                        f"REF: {ct.get('referencia') or '—'} · PED: {ct.get('pedimento') or '—'}</div>",
                        unsafe_allow_html=True)
                    # Foco T3 (semáforo): verde/rojo/azul, apagado si no tiene
                    _t3 = (ct.get("modulo_t3") or "").strip().upper()
                    _foco = {"VERDE": ("#3ddc84", "VERDE"), "ROJO": ("#ff6b6b", "ROJO"),
                             "BLOQUEADO": ("#4a90d9", "BLOQUEADO")}.get(_t3)
                    if _foco:
                        _fc, _ft = _foco
                        _t3_html = (f"<span style='display:inline-block;width:11px;height:11px;border-radius:50%;"
                                    f"background:{_fc};box-shadow:0 0 6px {_fc};margin-right:6px;vertical-align:middle'></span>"
                                    f"<span style='font-size:0.72rem;color:#cfcfcf'>T3: {_ft}</span>")
                    else:
                        _t3_html = ("<span style='display:inline-block;width:11px;height:11px;border-radius:50%;"
                                    "background:#3a3f47;margin-right:6px;vertical-align:middle'></span>"
                                    "<span style='font-size:0.72rem;color:#6b7280'>T3: —</span>")
                    cols[1].markdown(f"CLIENTE: {ct.get('cliente') or '—'}  \nETA: {ct.get('eta') or '—'}")
                    cols[1].markdown(_t3_html, unsafe_allow_html=True)
                    # Estatus pintado (vacío = SIN ESTATUS, en gris)
                    est_raw = (ct.get("estatus") or "").strip()
                    est_act = est_raw if est_raw else "SIN ESTATUS"
                    color = reglas.color_estatus(est_raw)
                    cols[2].markdown(
                        f"<div style='background:{color};color:#fff;padding:6px 10px;border-radius:6px;"
                        f"text-align:center;font-weight:700;font-size:0.8rem'>{est_act}</div>",
                        unsafe_allow_html=True)
                    if es_admin:
                        if cols[3].button("🗑️", key=f"del_{ct['id']}", help="Eliminar", type="secondary"):
                            st.session_state[f"borrando_{ct['id']}"] = True
                    # Pedir motivo al eliminar
                    if es_admin and st.session_state.get(f"borrando_{ct['id']}"):
                        motivo = st.text_input("Motivo de la eliminación",
                                               key=f"motivo_{ct['id']}",
                                               placeholder="¿Por qué se elimina?")
                        mc = st.columns(2)
                        if mc[0].button("Confirmar eliminación", type="primary", key=f"delok_{ct['id']}"):
                            if not motivo.strip():
                                st.warning("El motivo es obligatorio.")
                            else:
                                _sello = datetime.now().strftime("%d/%m/%Y %H:%M")
                                _motivo_full = reglas.normalizar_texto(motivo) + f"  [{_sello}]"
                                datos.eliminar_contenedor(ct["id"], actor, _motivo_full)
                                st.session_state[f"borrando_{ct['id']}"] = False
                                st.rerun()
                        if mc[1].button("Cancelar", key=f"delno_{ct['id']}"):
                            st.session_state[f"borrando_{ct['id']}"] = False
                            st.rerun()
                    # Confirmación de guardado (persiste tras cerrar la ficha)
                    if st.session_state.get(f"msg_guardado_{ct['id']}"):
                        st.success(st.session_state[f"msg_guardado_{ct['id']}"])
                        del st.session_state[f"msg_guardado_{ct['id']}"]
                    # Ficha de edición (se abre al clic en el contenedor)
                    if st.session_state.get(f"editando_{ct['id']}"):
                        _ficha_edicion(ct, actor, es_admin)


# ---------- BÚSQUEDA GLOBAL ----------
def panel_busqueda():
    st.subheader("🔎 BUSCAR EN TODAS LAS ADUANAS")
    st.caption("Busca por contenedor, cliente o estatus. Muestra resultados de Pantaco, Manzanillo y Lázaro.")
    st.markdown("<div style='margin:0.5rem 0 1rem'></div>", unsafe_allow_html=True)
    c_tipo, c_campo = st.columns([1, 3])
    tipo = c_tipo.selectbox("Buscar por", ["Contenedor", "Referencia", "Cliente", "Estatus"],
                            key="tipo_busqueda")

    resultados = None
    if tipo == "Contenedor":
        termino = c_campo.text_input("Número de contenedor", key="busqueda_global",
                                     max_chars=11,
                                     placeholder="Escribe el número de contenedor (11 caracteres)")
        if not termino.strip():
            return
        limpio = reglas.limpiar_contenedor(termino)
        resultados = datos.buscar_por_contenedor(limpio)

    elif tipo == "Referencia":
        termino = c_campo.text_input("Referencia", key="busqueda_ref",
                                     placeholder="Pega o escribe la referencia")
        # limpiar espacios al inicio y final automáticamente (común al copiar/pegar)
        ref_limpia = (termino or "").strip()
        if not ref_limpia:
            return
        resultados = datos.buscar_por_referencia(ref_limpia)

    elif tipo == "Cliente":
        clientes = datos.listar_catalogo("CLIENTE")
        cli_sel = c_campo.selectbox("Cliente", ["(seleccionar)"] + clientes,
                                    key="busc_cli")
        if cli_sel == "(seleccionar)":
            return
        fc1, fc2 = st.columns(2)
        f_aduana = fc1.selectbox("Filtrar aduana", ["TODAS", "PANTACO", "MANZANILLO", "LAZARO"], key="f_aduana")
        f_estatus = fc2.selectbox("Filtrar estatus", ["TODOS"] + datos.estatus_existentes(), key="f_estatus")
        resultados = datos.buscar_por_cliente(
            cli_sel,
            aduana=None if f_aduana == "TODAS" else f_aduana,
            estatus=None if f_estatus in ("TODOS", "(vacío)") else f_estatus)

    else:  # Estatus
        est_disp = datos.estatus_existentes()
        est_sel = c_campo.multiselect("Estatus (puedes elegir varios)", est_disp,
                                      key="busc_est",
                                      placeholder="Toca cada estatus que quieras ver (se van sumando)")
        if not est_sel:
            return
        fa = st.selectbox("Filtrar aduana", ["TODAS", "PANTACO", "MANZANILLO", "LAZARO"], key="f_aduana_est")
        # Convertir "(vacío)" a ""
        estatus_q = ["" if e == "(vacío)" else e for e in est_sel]
        resultados = datos.buscar_por_estatus(estatus_q,
                                              aduana=None if fa == "TODAS" else fa)

    if resultados is None:
        return
    if not resultados:
        st.info("Sin resultados.")
        return
    st.caption(f"{len(resultados)} resultado(s)")
    nombres_aduana = {"PANTACO": "Pantaco", "MANZANILLO": "Manzanillo", "LAZARO": "Lázaro"}
    for r in resultados:
        color = reglas.color_estatus(r.get("estatus"))
        with st.container(border=True):
            a, b, c = st.columns([2, 2, 1.5])
            a.markdown(
                f"<div style='font-size:1.1rem;font-weight:800'>{r['contenedor']}</div>"
                f"<div style='font-size:0.7rem;color:#9aa0a6'>REF: {r.get('referencia') or '—'} · "
                f"PED: {r.get('pedimento') or '—'}</div>", unsafe_allow_html=True)
            b.markdown(f"CLIENTE: {r.get('cliente') or '—'}  \n"
                       f"ADUANA: {nombres_aduana.get(r['aduana'], r['aduana'])}")
            c.markdown(
                f"<div style='background:{color};color:#fff;padding:3px 8px;border-radius:5px;"
                f"text-align:center;font-weight:700;font-size:0.78rem'>{(r.get('estatus') or '').strip() or 'SIN ESTATUS'}</div>"
                f"<div style='font-size:0.72rem;color:#9aa0a6;margin-top:3px'>ETA: {r.get('eta') or '—'}</div>",
                unsafe_allow_html=True)


# ---------- PANEL BASE (catálogos, solo admin) ----------
def panel_base():
    actor = st.session_state.usuario["usuario"]
    st.subheader("BASE · Catálogos de validación")

    # --- CARGA TEMPORAL DE PRUEBA (eliminar en una semana) ---
    with st.expander("⏳ CARGA DE PRUEBA: Pantaco 2026 (temporal)", expanded=False):
        st.caption("Carga los 148 registros 2026 de Pantaco para pruebas. Una sola vez.")
        import json as _j, os as _o
        ruta = _o.path.join(_o.path.dirname(__file__), "carga_pantaco_2026.json")
        if st.button("Cargar Pantaco 2026", key="carga_test"):
            if _o.path.exists(ruta):
                with open(ruta, encoding="utf-8") as _f:
                    regs = _j.load(_f)
                n = datos.cargar_pantaco_2026(regs, actor)
                st.success(f"Cargados {n} registros." if n else "Ya había datos, no se recargó.")
                st.rerun()
            else:
                st.error("No se encontró el archivo de carga.")

    st.caption("Aquí administras las listas que aparecen en los formularios. "
               "Igual que la hoja BASE de tu Excel.")

    tipos = datos.tipos_catalogo()

    # Agregar valor a un catálogo existente
    with st.expander("➕ AGREGAR DATO A UN CATÁLOGO", expanded=False):
        c1, c2 = st.columns(2)
        tipo_sel = c1.selectbox("Catálogo", tipos, key="base_tipo")
        nuevo_val = c2.text_input("Nuevo valor", key="base_val")
        if st.button("Agregar dato", type="primary", key="base_add"):
            if nuevo_val.strip():
                ok, msg = datos.agregar_valor_catalogo(tipo_sel, nuevo_val, actor)
                _ = st.success(msg) if ok else st.warning(msg)
                if ok: st.rerun()
            else:
                st.warning("Escribe un valor.")

    # Crear catálogo nuevo (columna nueva)
    with st.expander("🆕 CREAR CATÁLOGO NUEVO (columna nueva)", expanded=False):
        nuevo_tipo = st.text_input("Nombre del nuevo catálogo", key="base_nuevotipo")
        if st.button("Crear catálogo", type="primary", key="base_newtype"):
            if nuevo_tipo.strip():
                ok, msg = datos.crear_tipo_catalogo(nuevo_tipo, actor)
                _ = st.success(msg) if ok else st.warning(msg)
                if ok: st.rerun()

    # Ver catálogos
    st.markdown("##### Catálogos actuales")
    tipo_ver = st.selectbox("Ver catálogo", tipos, key="base_ver")
    valores = datos.listar_catalogo(tipo_ver)
    st.caption(f"{len(valores)} valores en {tipo_ver}")
    if valores:
        for i, v in enumerate(valores, 1):
            st.markdown(f"{i}. {v}")
    else:
        st.caption("(vacío)")


# ---------- RUTEO ----------
if st.session_state.usuario is None:
    pantalla_login()
else:
    # Botón Salir arriba a la derecha
    top = st.columns([6, 1])
    with top[1]:
        if st.button("Salir ⏻"):
            st.session_state.usuario = None; st.rerun()
    header()
    u = st.session_state.usuario

    if u["rol"] == "Administrador":
        t_busc, t_pan, t1, t_base, t2, t_rep = st.tabs(
            ["🔎 Buscar", "🚛 Pantaco", "👥 Usuarios", "🗂️ Base", "🕓 Historial", "📊 Reportes"])
        with t_busc: panel_busqueda()
        with t_pan: panel_aduana("PANTACO", "Pantaco")
        with t1: panel_usuarios()
        with t_base: panel_base()
        with t2: panel_historial()
        with t_rep: panel_reportes()
    elif u["rol"] == "Consulta":
        # Solo lectura: únicamente la pestaña Buscar, ve todo pero no modifica
        panel_busqueda()
    elif u["rol"] == "Supervisión":
        # Supervisión: Buscar y Pantaco. Usuarios SOLO si el admin le dio ese permiso.
        usr = datos.obtener_usuario_por_username(u["usuario"])
        gestiona = usr and datos.puede_gestionar_usuarios(usr["id"])
        if gestiona:
            t_busc, t_pan, t_us, t_rep = st.tabs(["🔎 Buscar", "🚛 Pantaco", "👥 Usuarios", "📊 Reportes"])
            with t_busc: panel_busqueda()
            with t_pan: panel_aduana("PANTACO", "Pantaco")
            with t_us: panel_usuarios()
            with t_rep: panel_reportes()
        else:
            t_busc, t_pan, t_rep = st.tabs(["🔎 Buscar", "🚛 Pantaco", "📊 Reportes"])
            with t_busc: panel_busqueda()
            with t_pan: panel_aduana("PANTACO", "Pantaco")
            with t_rep: panel_reportes()
    else:
        # Los demás roles operativos: buscar y su panel de aduana
        t_busc, t_pan = st.tabs(["🔎 Buscar", "🚛 Pantaco"])
        with t_busc: panel_busqueda()
        with t_pan: panel_aduana("PANTACO", "Pantaco")

# Pintar el cesto de eliminar en naranja (componente que sí alcanza el documento de la app)
st.components.v1.html("""
<script>
function pintarCestos(){
  try {
    const doc = window.parent.document;
    doc.querySelectorAll('button').forEach(b => {
      const t = (b.innerText || '').trim();
      if(t === '🗑️'){
        b.style.setProperty('background', '#b07a4a', 'important');
        b.style.setProperty('border-color', '#c98a55', 'important');
        b.style.setProperty('color', '#fff', 'important');
      }
    });
  } catch(e){}
}
setInterval(pintarCestos, 400);
pintarCestos();
</script>
""", height=0)
