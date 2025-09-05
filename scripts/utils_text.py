import re
import unicodedata


def strip_accents(s: str) -> str:
    if s is None:
        return s
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c))


def to_snake(s: str) -> str:
    if s is None:
        return s
    s = strip_accents(s).lower().strip()
    s = s.replace("ñ", "n")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def clean_whitespace(s: str) -> str:
    if s is None:
        return s
    return re.sub(r"\s+", " ", str(s)).strip()


def normalize_token(s: str) -> str:
    """Normaliza 'Sin dato' y variantes a una forma estándar."""
    if s is None:
        return None
    val = clean_whitespace(str(s)).lower()
    if val in {"sin dato", "sindato", "sin  dato", "n.a.", "na", "n.a", "n.a"}:
        return None
    return s
