"""
RUCO - Motor de reglas de negocio.
Esta pieza es INDEPENDIENTE de la pantalla. Aquí viven las reglas duras.
Si algún día cambiamos la interfaz, este archivo se reusa tal cual.
"""
import re
from datetime import datetime

# Catálogo de aduanas: clave -> (nombre, prefijo de consecutivo)
ADUANAS = {
    "PANTACO": ("Pantaco", "PN"),
    "MANZANILLO": ("Manzanillo", "MZ"),
    "LAZARO": ("Lázaro", "LZ"),
}

# Estatus oficiales (catálogo cerrado, normalizado)
ESTATUS = [
    "CAPTURA", "ANALISIS", "REVISION", "GLOSA", "PAGADO", "OK OPERACIONES",
    "DESPACHADO", "MODULADO", "RETENIDO", "PAMA", "ABANDONO", "DESISTIDO", "CANCELADO",
]

# --- REGLA DE ORO 1: validación del contenedor ---
def limpiar_contenedor(valor: str) -> str:
    """Quita espacios y pasa a mayúsculas ANTES de cualquier validación."""
    if valor is None:
        return ""
    return str(valor).strip().upper().replace(" ", "")

def validar_contenedor(valor: str):
    """
    Devuelve (es_valido, mensaje).
    Un contenedor es 4 letras + 7 dígitos = 11 caracteres exactos.
    """
    limpio = limpiar_contenedor(valor)
    if len(limpio) != 11:
        return False, f"Debe tener 11 caracteres (tiene {len(limpio)})."
    if not re.match(r"^[A-Z]{4}[0-9]{7}$", limpio):
        return False, "Formato inválido: deben ser 4 letras seguidas de 7 dígitos."
    return True, "OK"

# --- REGLA DE ORO 2: consecutivo por aduana y año real ---
def generar_consecutivo(aduana: str, anio: int, ultimo_folio: int) -> str:
    """
    Formato AD-AA####. El año lo marca la operación real, no la fecha de subida.
    ultimo_folio = el folio más alto ya usado en esa aduana ese año (0 si ninguno).
    """
    prefijo = ADUANAS[aduana][1]
    aa = str(anio)[-2:]  # 2025 -> '25'
    folio = ultimo_folio + 1
    return f"{prefijo}-{aa}{folio:04d}"

# --- REGLA DE ORO 3: duplicados por ventana de 3 meses ---
def evaluar_duplicado(meses_desde_ultimo):
    """
    meses_desde_ultimo = None si el contenedor nunca existió.
    Devuelve uno de: 'NUEVO', 'REINGRESO', 'DUDOSO'.
    """
    if meses_desde_ultimo is None:
        return "NUEVO"
    if meses_desde_ultimo >= 3:
        return "REINGRESO"
    return "DUDOSO"  # requiere autorización del administrador


# --- Helper: meses entre dos fechas ISO ---
def meses_entre(fecha_iso_anterior, fecha_iso_ahora=None):
    """Calcula cuántos meses pasaron entre dos fechas. None si no hay fecha anterior."""
    from datetime import datetime
    if not fecha_iso_anterior:
        return None
    try:
        ant = datetime.fromisoformat(str(fecha_iso_anterior))
    except Exception:
        return None
    ahora = datetime.fromisoformat(fecha_iso_ahora) if fecha_iso_ahora else datetime.now()
    return (ahora.year - ant.year) * 12 + (ahora.month - ant.month)


# --- Normalizador de texto para campos ---
def normalizar_texto(valor):
    """Mayúsculas, sin acentos, conserva Ñ. Para todo lo que se escribe en campos."""
    if valor is None:
        return ""
    import unicodedata
    s = str(valor).upper().strip()
    # Proteger la Ñ antes de quitar acentos
    s = s.replace("Ñ", "\x00")
    # Quitar acentos
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # Restaurar Ñ
    s = s.replace("\x00", "Ñ")
    return s
