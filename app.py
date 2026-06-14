"""
RUCO - Interfaz (la cara que la gente usa).
Esta pieza es solo presentación. Toda la lógica vive en core/.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from core import datos, reglas

st.set_page_config(page_title="RUCO", page_icon="📦", layout="wide")

datos.inicializar()


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

def panel_aduana(aduana_key, aduana_nombre):
    actor = st.session_state.usuario["usuario"]
    es_admin = st.session_state.usuario["rol"] == "Administrador"
    st.subheader(f"CONTENEDORES · {aduana_nombre.upper()}")

    # Forzar mayúsculas y límite de 11 en el campo de contenedor (JS en el navegador)
    st.markdown("""
    <script>
    const aplicar = () => {
      const inputs = window.parent.document.querySelectorAll('input');
      inputs.forEach(inp => {
        if(inp.dataset.rucoCont) {
          inp.setAttribute('maxlength','11');
          inp.value = inp.value.toUpperCase().replace(/\\s/g,'');
        }
      });
    };
    setInterval(aplicar, 300);
    </script>
    """, unsafe_allow_html=True)

    # --- Alta mínima ---
    with st.expander("➕ DAR DE ALTA UN CONTENEDOR", expanded=False):
        c1, c2 = st.columns(2)
        cont_raw = c1.text_input("NÚMERO DE CONTENEDOR", max_chars=11,
                                 key=f"alta_cont_{aduana_key}",
                                 help="11 caracteres: 4 letras + 7 dígitos")
        cliente = c2.text_input("CLIENTE", key=f"alta_cli_{aduana_key}")
        if st.button("DAR DE ALTA", type="primary", key=f"alta_btn_{aduana_key}"):
            # Regla de oro 1: limpiar y validar
            limpio = reglas.limpiar_contenedor(cont_raw)
            ok, msg = reglas.validar_contenedor(cont_raw)
            cliente_norm = reglas.normalizar_texto(cliente)
            if not cliente_norm:
                st.warning("El cliente es obligatorio.")
            elif not ok:
                st.error(f"Contenedor inválido: {msg}")
            else:
                # Regla de oro 3: duplicados por ventana de 3 meses
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

    # --- Lista de contenedores ---
    conts = datos.listar_contenedores(aduana_key)
    if not conts:
        st.info("Aún no hay contenedores capturados en esta aduana.")
        return
    st.markdown(f"##### {len(conts)} CONTENEDORES")
    for ct in conts:
        with st.container(border=True):
            cols = st.columns([2, 2, 1.4, 0.8]) if es_admin else st.columns([2, 2, 1.4])
            cols[0].markdown(f"**{ct['consecutivo']}**  \n`{ct['contenedor']}`")
            cols[1].markdown(f"CLIENTE: {ct.get('cliente') or '—'}  \nETA: {ct.get('eta') or '—'}")
            estatus_actual = ct.get("estatus") or "CAPTURA"
            nuevo_est = cols[2].selectbox("ESTATUS", reglas.ESTATUS,
                index=reglas.ESTATUS.index(estatus_actual) if estatus_actual in reglas.ESTATUS else 0,
                key=f"est_{ct['id']}")
            if nuevo_est != estatus_actual:
                datos.actualizar_campo_contenedor(ct["id"], "estatus", nuevo_est, actor)
                st.rerun()
            # Solo admin ve eliminar
            if es_admin:
                if cols[3].button("🗑️", key=f"del_{ct['id']}", help="Eliminar (solo admin)"):
                    datos.eliminar_contenedor(ct["id"], actor)
                    st.rerun()


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
        t_pan, t1, t2 = st.tabs(["📦 Pantaco", "👥 Usuarios", "🕓 Historial"])
        with t_pan: panel_aduana("PANTACO", "Pantaco")
        with t1: panel_usuarios()
        with t2: panel_historial()
    else:
        st.info(f"Hola {u['nombre']}. Tu panel de **{u['rol']}** se construirá en las siguientes fases.")
