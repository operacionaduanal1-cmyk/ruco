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

    with st.expander("➕ Crear nuevo usuario", expanded=False):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre completo")
        usuario = c2.text_input("Usuario (para entrar)")
        c3, c4 = st.columns(2)
        password = c3.text_input("Contraseña inicial", type="password")
        rol = c4.selectbox("Área / Rol", datos.listar_roles())
        cliente = ""
        if rol == "Consulta cliente":
            cliente = st.text_input("Cliente ligado (solo verá lo de este cliente)")
        if st.button("Crear usuario", type="primary"):
            if not (nombre and usuario and password):
                st.warning("Llena nombre, usuario y contraseña.")
            elif rol == "Consulta cliente" and not cliente:
                st.warning("Un usuario de consulta cliente necesita el cliente ligado.")
            else:
                ok, msg = datos.crear_usuario(nombre, usuario, password, rol, cliente, actor)
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

    st.markdown("##### Usuarios registrados")
    for u in datos.listar_usuarios():
        c1, c2, c3, c4 = st.columns([2.5, 2, 1.3, 1])
        estado = "<span class='badge-on'>● Activo</span>" if u["activo"] else "<span class='badge-off'>○ Inactivo</span>"
        ligado = f" · cliente: {u['cliente_ligado']}" if u["cliente_ligado"] else ""
        c1.markdown(f"**{u['nombre']}**  \n`{u['usuario']}`")
        c2.markdown(f"{u['rol']}{ligado}")
        c3.markdown(estado, unsafe_allow_html=True)
        if u["rol"] != "Administrador" or u["usuario"] != "admin":
            if u["activo"]:
                if c4.button("Desactivar", key=f"off{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], False, actor); st.rerun()
            else:
                if c4.button("Activar", key=f"on{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], True, actor); st.rerun()

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

# ---------- PANEL ADUANA: PANTACO ----------
datos.inicializar_contenedores()

def _ficha_edicion(ct, actor, es_admin):
    """Ficha de edición completa de un contenedor (admin edita todo)."""
    st.markdown(f"#### Editar {ct['consecutivo']} · {ct['contenedor']}")
    clientes = ["(sin cambio)"] + datos.listar_catalogo("CLIENTE")
    importadores = ["(sin cambio)"] + datos.listar_catalogo("IMPORTADOR")
    aas = ["(sin cambio)"] + datos.listar_catalogo("AA")
    regimenes = ["(sin cambio)"] + datos.listar_catalogo("REGIMEN")
    detalles = ["(sin cambio)"] + datos.listar_catalogo("DETALLE")

    c1, c2, c3 = st.columns(3)
    nuevo_cliente = c1.selectbox("CLIENTE", clientes, key=f"ed_cli_{ct['id']}")
    nuevo_imp = c2.selectbox("IMPORTADOR", importadores, key=f"ed_imp_{ct['id']}")
    nuevo_aa = c3.selectbox("AGENTE ADUANAL", aas, key=f"ed_aa_{ct['id']}")

    c4, c5, c6 = st.columns(3)
    nueva_ref = c4.text_input("REFERENCIA", value=ct.get("referencia") or "", key=f"ed_ref_{ct['id']}")
    nuevo_ped = c5.text_input("PEDIMENTO", value=ct.get("pedimento") or "", key=f"ed_ped_{ct['id']}")
    nueva_eta = c6.text_input("ETA", value=ct.get("eta") or "", key=f"ed_eta_{ct['id']}")

    c7, c8, c9 = st.columns(3)
    nuevo_reg = c7.selectbox("REGIMEN", regimenes, key=f"ed_reg_{ct['id']}")
    nuevo_det = c8.selectbox("DETALLE", detalles, key=f"ed_det_{ct['id']}")
    nueva_fpago = c9.text_input("FECHA DE PAGO", value=ct.get("fecha_pago") or "", key=f"ed_fp_{ct['id']}")

    nuevo_t3 = st.selectbox("MODULO T3", ["(sin cambio)"] + datos.listar_catalogo("T3"), key=f"ed_t3_{ct['id']}")
    nuevas_obs = st.text_area("OBSERVACIONES", value=ct.get("observaciones") or "", key=f"ed_obs_{ct['id']}")

    if st.button("Guardar cambios", type="primary", key=f"ed_save_{ct['id']}"):
        cambios = []
        def aplicar(campo, valor, normaliza=True):
            if valor and valor != "(sin cambio)":
                v = reglas.normalizar_texto(valor) if normaliza else valor
                datos.actualizar_campo_contenedor(ct["id"], campo, v, actor)
                cambios.append(campo)
        aplicar("cliente", nuevo_cliente)
        aplicar("importador", nuevo_imp)
        aplicar("aa", nuevo_aa)
        aplicar("referencia", nueva_ref)
        aplicar("pedimento", nuevo_ped)
        aplicar("eta", nueva_eta)
        aplicar("regimen", nuevo_reg)
        aplicar("detalle", nuevo_det)
        aplicar("fecha_pago", nueva_fpago)
        aplicar("modulo_t3", nuevo_t3)
        aplicar("observaciones", nuevas_obs)
        st.success(f"Guardado ({len(cambios)} campos).")
        st.session_state[f"editando_{ct['id']}"] = False
        st.rerun()
    if st.button("Cerrar", key=f"ed_close_{ct['id']}"):
        st.session_state[f"editando_{ct['id']}"] = False
        st.rerun()


def panel_aduana(aduana_key, aduana_nombre):
    actor = st.session_state.usuario["usuario"]
    es_admin = st.session_state.usuario["rol"] == "Administrador"
    st.subheader(f"CONTENEDORES · {aduana_nombre.upper()}")

    # --- Alta mínima ---
    with st.expander("➕ DAR DE ALTA UN CONTENEDOR", expanded=False):
        c1, c2 = st.columns(2)
        cont_raw = c1.text_input("NÚMERO DE CONTENEDOR", max_chars=11,
                                 key=f"alta_cont_{aduana_key}",
                                 help="11 caracteres: 4 letras + 7 dígitos")
        clientes_cat = datos.listar_catalogo("CLIENTE")
        cliente_sel = c2.selectbox("CLIENTE", ["(escribir nuevo)"] + clientes_cat,
                                   key=f"alta_clisel_{aduana_key}")
        cliente_nuevo = ""
        if cliente_sel == "(escribir nuevo)":
            cliente_nuevo = st.text_input("Nuevo cliente", key=f"alta_clinew_{aduana_key}")
        if st.button("DAR DE ALTA", type="primary", key=f"alta_btn_{aduana_key}"):
            limpio = reglas.limpiar_contenedor(cont_raw)
            ok, msg = reglas.validar_contenedor(cont_raw)
            cliente_final = cliente_nuevo if cliente_sel == "(escribir nuevo)" else cliente_sel
            cliente_norm = reglas.normalizar_texto(cliente_final)
            if not cliente_norm:
                st.warning("El cliente es obligatorio.")
            elif not ok:
                st.error(f"Contenedor inválido: {msg}")
            else:
                previo = datos.buscar_contenedor_existente(limpio)
                clasif = "NUEVO"
                if previo:
                    m = reglas.meses_entre(previo.get("creado"))
                    clasif = reglas.evaluar_duplicado(m)
                if clasif == "DUDOSO":
                    st.error(f"⚠️ El contenedor {limpio} ya existe con menos de 3 meses "
                             f"(consecutivo {previo.get('consecutivo')}). "
                             f"Posible duplicado. Requiere autorización del administrador.")
                else:
                    # Si el cliente es nuevo, agregarlo al catálogo
                    if cliente_sel == "(escribir nuevo)" and cliente_norm not in clientes_cat:
                        datos.agregar_valor_catalogo("CLIENTE", cliente_norm, actor)
                    anio = datetime.now().year
                    folio = datos.ultimo_folio(aduana_key, anio) + 1
                    consec = reglas.generar_consecutivo(aduana_key, anio, folio - 1)
                    datos.crear_contenedor(aduana_key, limpio, cliente_norm,
                                           consec, anio, folio, actor)
                    if clasif == "REINGRESO":
                        st.success(f"Reingreso registrado: {consec} · {limpio} (+3 meses).")
                    else:
                        st.success(f"Contenedor dado de alta: {consec} · {limpio}")
                    st.rerun()

    # --- Lista de contenedores (colapsada, paginada para no cargar todo) ---
    total = datos.contar_contenedores(aduana_key)
    with st.expander(f"📋 VER LISTA DE CONTENEDORES ({total})", expanded=False):
        if total == 0:
            st.info("Aún no hay contenedores capturados en esta aduana.")
            return
        POR_PAGINA = 20
        npag = (total - 1) // POR_PAGINA + 1
        pag = st.number_input("Página", min_value=1, max_value=npag, value=1,
                              key=f"pag_{aduana_key}")
        st.caption(f"Mostrando página {pag} de {npag} ({POR_PAGINA} por página)")
        conts = datos.listar_contenedores(aduana_key, limite=POR_PAGINA,
                                          offset=(pag - 1) * POR_PAGINA)
        for ct in conts:
            with st.container(border=True):
                cols = st.columns([2, 2, 1.4, 0.6, 0.6]) if es_admin else st.columns([2, 2, 1.4])
                cols[0].markdown(f"**{ct['consecutivo']}**  \n`{ct['contenedor']}`")
                cols[1].markdown(f"CLIENTE: {ct.get('cliente') or '—'}  \nETA: {ct.get('eta') or '—'}")
                estatus_actual = ct.get("estatus") or "CAPTURA"
                nuevo_est = cols[2].selectbox("ESTATUS", reglas.ESTATUS,
                    index=reglas.ESTATUS.index(estatus_actual) if estatus_actual in reglas.ESTATUS else 0,
                    key=f"est_{ct['id']}")
                if nuevo_est != estatus_actual:
                    datos.actualizar_campo_contenedor(ct["id"], "estatus", nuevo_est, actor)
                    st.rerun()
                if es_admin:
                    if cols[3].button("✏️", key=f"edit_{ct['id']}", help="Editar todo"):
                        st.session_state[f"editando_{ct['id']}"] = True
                    if cols[4].button("🗑️", key=f"del_{ct['id']}", help="Eliminar (solo admin)"):
                        datos.eliminar_contenedor(ct["id"], actor)
                        st.rerun()
                # Ficha de edición desplegada
                if es_admin and st.session_state.get(f"editando_{ct['id']}"):
                    _ficha_edicion(ct, actor, es_admin)


# ---------- BÚSQUEDA GLOBAL ----------
def panel_busqueda():
    st.markdown("<div style='margin:0.5rem 0 1rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    termino = c1.text_input("🔎 BUSCAR", key="busqueda_global",
                            placeholder="Número de contenedor o nombre de cliente",
                            label_visibility="collapsed")
    tipo = c2.selectbox("Tipo", ["Contenedor", "Cliente"], key="tipo_busqueda",
                        label_visibility="collapsed")
    if not termino.strip():
        return

    if tipo == "Contenedor":
        limpio = reglas.limpiar_contenedor(termino)
        resultados = datos.buscar_por_contenedor(limpio)
    else:
        # Filtros adicionales para búsqueda por cliente
        fc1, fc2 = st.columns(2)
        f_aduana = fc1.selectbox("Filtrar aduana", ["TODAS", "PANTACO", "MANZANILLO", "LAZARO"],
                                 key="f_aduana")
        f_estatus = fc2.selectbox("Filtrar estatus", ["TODOS"] + reglas.ESTATUS, key="f_estatus")
        resultados = datos.buscar_por_cliente(
            reglas.normalizar_texto(termino),
            aduana=None if f_aduana == "TODAS" else f_aduana,
            estatus=None if f_estatus == "TODOS" else f_estatus)

    if not resultados:
        st.info("Sin resultados.")
        return
    st.caption(f"{len(resultados)} resultado(s)")
    nombres_aduana = {"PANTACO": "Pantaco", "MANZANILLO": "Manzanillo", "LAZARO": "Lázaro"}
    for r in resultados:
        with st.container(border=True):
            a, b, c = st.columns([1.5, 2, 1.5])
            a.markdown(f"**{r['consecutivo']}**  \n`{r['contenedor']}`")
            b.markdown(f"CLIENTE: {r.get('cliente') or '—'}  \n"
                       f"ADUANA: {nombres_aduana.get(r['aduana'], r['aduana'])}")
            c.markdown(f"ESTATUS: **{r.get('estatus') or '—'}**  \nETA: {r.get('eta') or '—'}")


# ---------- PANEL BASE (catálogos, solo admin) ----------
def panel_base():
    actor = st.session_state.usuario["usuario"]
    st.subheader("BASE · Catálogos de validación")
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
                st.success(msg) if ok else st.warning(msg)
                if ok: st.rerun()
            else:
                st.warning("Escribe un valor.")

    # Crear catálogo nuevo (columna nueva)
    with st.expander("🆕 CREAR CATÁLOGO NUEVO (columna nueva)", expanded=False):
        nuevo_tipo = st.text_input("Nombre del nuevo catálogo", key="base_nuevotipo")
        if st.button("Crear catálogo", type="primary", key="base_newtype"):
            if nuevo_tipo.strip():
                ok, msg = datos.crear_tipo_catalogo(nuevo_tipo, actor)
                st.success(msg) if ok else st.warning(msg)
                if ok: st.rerun()

    # Ver catálogos
    st.markdown("##### Catálogos actuales")
    tipo_ver = st.selectbox("Ver catálogo", tipos, key="base_ver")
    valores = datos.listar_catalogo(tipo_ver)
    st.caption(f"{len(valores)} valores en {tipo_ver}")
    st.write(", ".join(valores) if valores else "(vacío)")


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

    # Barra de búsqueda debajo del logo
    panel_busqueda()

    if u["rol"] == "Administrador":
        t_pan, t1, t_base, t2 = st.tabs(["📦 Pantaco", "👥 Usuarios", "🗂️ Base", "🕓 Historial"])
        with t_pan: panel_aduana("PANTACO", "Pantaco")
        with t1: panel_usuarios()
        with t_base: panel_base()
        with t2: panel_historial()
    else:
        st.info(f"Hola {u['nombre']}. Tu panel de **{u['rol']}** se construirá en las siguientes fases.")
