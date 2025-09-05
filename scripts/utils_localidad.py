from typing import Optional
import re
from utils_text import strip_accents, clean_whitespace


def fix_mojibake(s: str) -> str:
    """Intenta reparar mojibake típico (UTF-8 leído como Latin-1)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin1", errors="strict").decode("utf-8", errors="strict")
    except Exception:
        return s


# Correcciones específicas (mojibake y variantes comunes)
CORRECCIONES_ESPECIFICAS = {
    # Mojibake típicos CP1252/UTF-8
    "mÃ¡rtires": "mártires",
    "ciudad bol¡var": "ciudad bolívar",
    "fontib¢n": "fontibón",
    "usaqu‚n": "usaquén",
    "usaqun": "usaquén",
    "san crist¢bal": "san cristóbal",
    "antonio nari¤o": "antonio nariño",
    # Otros mojibake observados
    "antonio nariã±o": "antonio nariño",
    "ciudad bolã­var": "ciudad bolívar",
    # Variantes sin artículos
    "candelaria": "la candelaria",
    # Nombres oficiales
    "los mártires": "mártires",
}

# Listado de localidades oficiales de Bogotá (minúsculas, con tildes correctas)
LOCALIDADES_OFICIALES = {
    "usaquén", "chapinero", "santa fe", "san cristóbal", "usme", "tunjuelito",
    "bosa", "kennedy", "fontibón", "engativá", "suba", "barrios unidos",
    "teusaquillo", "los mártires", "antonio nariño", "puente aranda", "la candelaria",
    "rafael uribe uribe", "ciudad bolívar", "sumapaz",
}


def _sanitize_letters(s: str) -> str:
    """Conserva solo letras, espacios y caracteres acentuados básicos; colapsa espacios."""
    s = re.sub(r"[^a-záéíóúüñ\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_localidad(nombre: Optional[str]) -> Optional[str]:
    if not nombre or str(nombre).strip() == "":
        return None

    # Reparar mojibake, limpieza básica, a minúsculas
    s = fix_mojibake(str(nombre))
    s = clean_whitespace(s).lower()

    # Correcciones específicas y sanitización de caracteres raros
    s = CORRECCIONES_ESPECIFICAS.get(s, s)
    s = _sanitize_letters(s)

    # Mapeos de variantes comunes sin acento ni artículos (comparación sin acentos)
    s_no_acc = strip_accents(s).lower()
    variantes = {
        "candelaria": "la candelaria",
        "la candelaria": "la candelaria",
        "martires": "mártires",
        "los martires": "mártires",
        "los m rtires": "mártires",
        "mártires": "mártires",
        "ciudad bolivar": "ciudad bolívar",
        "san cristobal": "san cristóbal",
        "usaquen": "usaquén",
        "fontibon": "fontibón",
        "engativa": "engativá",
        "engativ": "engativá",
        "antonio narino": "antonio nariño",
        "antonio nariño": "antonio nariño",
        "rafael uribe": "rafael uribe uribe",
    }
    if s_no_acc in variantes:
        s = variantes[s_no_acc]

    # Validar contra listado oficial; si no coincide, devolver None para ser descartado
    if s not in LOCALIDADES_OFICIALES:
        return None
    return s
