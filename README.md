# RUCO — Reporte Único de Contenedores Oficial

Plataforma de seguimiento de contenedores de importación.
Reemplaza el Excel compartido por un sistema multiusuario con login,
permisos por área, historial de cambios y reglas de validación.

## Reglas de oro
1. Contenedor: 11 caracteres (4 letras + 7 dígitos), limpia espacios antes de validar.
2. Consecutivo por aduana y año real: PN/MZ/LZ + año + folio.
3. Duplicados por ventana de 3 meses (reingreso vs error).
4. Nunca se borra: solo se cancela con motivo en observaciones.

## Estructura
- `core/reglas.py` — motor de reglas (independiente de la pantalla)
- `core/datos.py` — capa de base de datos
- `app.py` — interfaz (Streamlit)
