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
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                if ok: st.rerun()

    st.markdown("##### Usuarios registrados")
    for u in datos.listar_usuarios():
        c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1.3, 1, 1])
        estado = "<span class='badge-on'>● Activo</span>" if u["activo"] else "<span class='badge-off'>○ Inactivo</span>"
        ligado = f" · cliente: {u['cliente_ligado']}" if u["cliente_ligado"] else ""
        c1.markdown(f"**{u['nombre']}**  \n`{u['usuario']}`")
        c2.markdown(f"{u['rol']}{ligado}")
        c3.markdown(estado, unsafe_allow_html=True)
        # No se puede tocar al admin principal
        if u["rol"] != "Administrador" or u["usuario"] != "admin":
            if u["activo"]:
                if c4.button("Desactivar", key=f"off{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], False, actor); st.rerun()
            else:
                if c4.button("Activar", key=f"on{u['id']}"):
                    datos.cambiar_estado_usuario(u["id"], True, actor); st.rerun()
            # Eliminar (con confirmación)
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

def _campo_fecha(label, valor, key):
    """Campo de fecha con formato dd/mm/yyyy guiado."""
    return st.text_input(label, value=valor or "", key=key,
                         placeholder="dd/mm/yyyy", max_chars=10)


def _ficha_edicion(ct, actor, es_admin):
    st.markdown(f"#### Editar {ct['consecutivo']} · {ct['contenedor']}")
    cli = ["(sin cambio)"] + datos.listar_catalogo("CLIENTE")
    imp = ["(sin cambio)"] + datos.listar_catalogo("IMPORTADOR")
    aas = ["(sin cambio)"] + datos.listar_catalogo("AA")
    regs = ["(sin cambio)"] + datos.listar_catalogo("REGIMEN")
    dets = ["(sin cambio)"] + datos.listar_catalogo("DETALLE")
    t3s = ["(sin cambio)"] + datos.listar_catalogo("T3")

    # Fila 1: cliente, importador, agente
    r1 = st.columns(3)
    n_cli = r1[0].selectbox("CLIENTE", cli, key=f"ed_cli_{ct['id']}")
    n_imp = r1[1].selectbox("IMPORTADOR", imp, key=f"ed_imp_{ct['id']}")
    n_aa = r1[2].selectbox("AGENTE ADUANAL", aas, key=f"ed_aa_{ct['id']}")
    # Fila 2: referencia, pedimento, ETA
    r2 = st.columns(3)
    n_ref = r2[0].text_input("REFERENCIA", value=ct.get("referencia") or "", key=f"ed_ref_{ct['id']}")
    n_ped = r2[1].text_input("PEDIMENTO", value=ct.get("pedimento") or "", key=f"ed_ped_{ct['id']}")
    n_eta = _campo_fecha("ETA", ct.get("eta"), f"ed_eta_{ct['id']}")
    # Fila 3: regimen, detalle, fecha pago
    r3 = st.columns(3)
    n_reg = r3[0].selectbox("REGIMEN", regs, key=f"ed_reg_{ct['id']}")
    n_det = r3[1].selectbox("DETALLE", dets, key=f"ed_det_{ct['id']}")
    n_fp = r3[2].text_input("FECHA DE PAGO", value=ct.get("fecha_pago") or "",
                            placeholder="dd/mm/yyyy", max_chars=10, key=f"ed_fp_{ct['id']}")
    # Fila 4: T3, observaciones
    n_t3 = st.selectbox("MODULO T3", t3s, key=f"ed_t3_{ct['id']}")
    n_obs = st.text_area("OBSERVACIONES", value=ct.get("observaciones") or "", key=f"ed_obs_{ct['id']}")

    if st.button("Guardar cambios", type="primary", key=f"ed_save_{ct['id']}"):
        # validar fechas
        ok_eta, msg_eta = reglas.validar_fecha(n_eta)
        ok_fp, msg_fp = reglas.validar_fecha(n_fp)
        if not ok_eta:
            st.error(f"ETA: {msg_eta}"); return
        if not ok_fp:
            st.error(f"FECHA DE PAGO: {msg_fp}"); return
        # validar referencia/pedimento si se llenaron
        if n_ref.strip():
            okr, vr = reglas.validar_referencia(n_ref)
            if not okr: st.error(f"REFERENCIA: {vr}"); return
            datos.actualizar_campo_contenedor(ct["id"], "referencia", vr, actor)
        if n_ped.strip():
            okp, vp = reglas.validar_pedimento(n_ped)
            if not okp: st.error(f"PEDIMENTO: {vp}"); return
            datos.actualizar_campo_contenedor(ct["id"], "pedimento", vp, actor)
        for campo, val in [("cliente",n_cli),("importador",n_imp),("aa",n_aa),
                           ("regimen",n_reg),("detalle",n_det),("modulo_t3",n_t3)]:
            if val and val != "(sin cambio)":
                datos.actualizar_campo_contenedor(ct["id"], campo, reglas.normalizar_texto(val), actor)
        if n_eta.strip(): datos.actualizar_campo_contenedor(ct["id"], "eta", n_eta.strip(), actor)
        if n_fp.strip(): datos.actualizar_campo_contenedor(ct["id"], "fecha_pago", n_fp.strip(), actor)
        if n_obs.strip(): datos.actualizar_campo_contenedor(ct["id"], "observaciones", reglas.normalizar_texto(n_obs), actor)
        st.success("Guardado.")
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
                    cols[1].markdown(f"CLIENTE: {ct.get('cliente') or '—'}  \nETA: {ct.get('eta') or '—'}")
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
                    # Ficha de edición (se abre al clic en el contenedor)
                    if st.session_state.get(f"editando_{ct['id']}"):
                        _ficha_edicion(ct, actor, es_admin)


# ---------- BÚSQUEDA GLOBAL ----------
def panel_busqueda():
    st.subheader("🔎 BUSCAR EN TODAS LAS ADUANAS")
    st.caption("Busca por contenedor, cliente o estatus. Muestra resultados de Pantaco, Manzanillo y Lázaro.")
    st.markdown("<div style='margin:0.5rem 0 1rem'></div>", unsafe_allow_html=True)
    c_tipo, c_campo = st.columns([1, 3])
    tipo = c_tipo.selectbox("Buscar por", ["Contenedor", "Cliente", "Estatus"],
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
        t_busc, t_pan, t1, t_base, t2 = st.tabs(
            ["🔎 Buscar", "🚛 Pantaco", "👥 Usuarios", "🗂️ Base", "🕓 Historial"])
        with t_busc: panel_busqueda()
        with t_pan: panel_aduana("PANTACO", "Pantaco")
        with t1: panel_usuarios()
        with t_base: panel_base()
        with t2: panel_historial()
    else:
        # Los demás roles: pueden buscar (ver todo lo pendiente) y su panel de aduana
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
