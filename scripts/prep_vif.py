import os
import re
import unicodedata
from typing import List

import numpy as np
import pandas as pd


RAW_PATH = os.path.join("data", "raw", "vintrafamiliar.csv")
WORKING_DIR = os.path.join("data", "working")
UTF8_EXPORT = os.path.join(WORKING_DIR, "vintrafamiliar_utf8.csv")
CLEAN_EXPORT = os.path.join(WORKING_DIR, "vintrafamiliar_clean.csv")
REPORT_PATH = os.path.join("docs", "prep_vif_report.md")


def ensure_dirs(paths: List[str]):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def slug_snake(name: str) -> str:
    """Normaliza nombres de columnas: snake_case, sin tildes, caracteres válidos."""
    if name is None:
        return name
    # Asegurar str
    s = str(name)
    # Quitar espacios extremos y normalizar unicode
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # quitar tildes
    s = s.strip().lower()
    # Reemplazos específicos comunes
    s = s.replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    # Sustituir no alfanumérico por guion bajo
    s = re.sub(r"[^a-z0-9]+", "_", s)
    # Quitar guiones bajos múltiples y bordes
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {c: slug_snake(c) for c in df.columns}
    # Ajustes puntuales del README
    mapping = {
        **mapping,
        "ano": "anio",
        "nombre_localidad": "nombre_localidad",  # ya en snake
        "grupoedad": "grupo_edad",
        "tipoaseguramiento": "tipo_aseguramiento",
        "entidadadministradora": "entidad_administradora",
        "agresor_consumospa": "agresor_consumo_spa",
        "victima_consumospa": "victima_consumo_spa",
        "lugocurrenciaemocional": "lugar_ocurrencia_emocional",
        "lugocurrenciafisica": "lugar_ocurrencia_fisica",
        "lugocurrenciasexual": "lugar_ocurrencia_sexual",
        "lugocurrenciaeconomica": "lugar_ocurrencia_economica",
        "lugocurrencianegligencia": "lugar_ocurrencia_negligencia",
        "lugocurrenciaabandono": "lugar_ocurrencia_abandono",
    }
    df = df.rename(columns=mapping)
    return df


def normalize_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica tokens de no respuesta y tipifica algunas columnas clave."""
    # Detectar variantes de "Sin dato" y espacios
    def is_sin_dato(x):
        if pd.isna(x):
            return True
        if not isinstance(x, str):
            return False
        s = x.strip().lower()
        return s in {"sin dato", "sindato", "sin  dato", "sin_dato"}

    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    for col in cat_cols:
        mask = df[col].apply(is_sin_dato)
        if mask.any():
            df.loc[mask, col] = np.nan

    # Variables binarias conocidas: 0/1 (no recodificar 0 a NA)
    for col in [
        "gestante",
        "agresor_consumo_spa",
        "victima_consumo_spa",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Estrato ordinal con no_reporta
    if "estrato" in df.columns:
        # Reemplazar NA por 'no_reporta' conservando enteros cuando existan
        df["estrato"] = (
            df["estrato"].astype(str).str.strip().replace({"nan": np.nan})
        )
        # Si es numérico convertible, mantener número, si no, no_reporta
        def parse_estrato(v):
            try:
                iv = int(float(v))
                if iv in {1, 2, 3, 4, 5, 6}:
                    return iv
            except Exception:
                pass
            return np.nan
        parsed = df["estrato"].apply(parse_estrato)
        df["estrato"] = parsed.astype("Int64")

    return df


def main():
    ensure_dirs([WORKING_DIR, os.path.dirname(REPORT_PATH)])

    print(f"Leyendo: {RAW_PATH} (latin1, sep=';')")
    df = pd.read_csv(RAW_PATH, encoding="latin1", sep=";", dtype=str, low_memory=False)

    # Exportar copia UTF-8 sin transformar (solo re-encoding)
    print(f"Exportando UTF-8: {UTF8_EXPORT}")
    df.to_csv(UTF8_EXPORT, index=False, encoding="utf-8")

    # Estandarizar columnas
    df = standardize_columns(df)

    # Tipificar y normalizar tokens
    df = normalize_tokens(df)

    # Tipos deseados adicionales
    for col in ["anio"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Guardar versión limpia
    print(f"Exportando versión limpia: {CLEAN_EXPORT}")
    df.to_csv(CLEAN_EXPORT, index=False, encoding="utf-8")

    # Reporte breve
    n_rows, n_cols = df.shape
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Reporte preparación VIF\n\n")
        f.write(f"Filas: {n_rows}, Columnas: {n_cols}\n\n")
        f.write("## Columnas\n\n")
        for c in df.columns:
            f.write(f"- {c}\n")
        f.write("\n## Muestras de valores\n\n")
        for c in df.columns[: min(10, n_cols)]:
            vals = df[c].dropna().astype(str).head(5).tolist()
            f.write(f"- {c}: {vals}\n")

    print("Listo. Ver archivos en data/working/ y reporte en docs/prep_vif_report.md")


if __name__ == "__main__":
    main()
