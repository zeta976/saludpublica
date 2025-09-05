import os
import pandas as pd
import numpy as np

from utils_text import to_snake, clean_whitespace, strip_accents
from utils_localidad import normalize_localidad

RAW_XLSX = os.path.join("data", "raw", "psicoactivas.xlsx")
WORKING_DIR = os.path.join("data", "working")
UTF8_EXPORT = os.path.join(WORKING_DIR, "psicoactivas_utf8.csv")
CLEAN_EXPORT = os.path.join(WORKING_DIR, "psicoactivas_clean.csv")
AGG_EXPORT = os.path.join(WORKING_DIR, "psicoactivas_localidad_anio.csv")
REPORT_PATH = os.path.join("docs", "prep_psicoactivas_report.md")


def ensure_dirs():
    os.makedirs(WORKING_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Paso 1: convertir todos los nombres a snake_case
    df = df.rename(columns={c: to_snake(c) for c in df.columns})
    # Paso 2: aplicar alias específicos sobre los nombres ya snake_case
    df = df.rename(columns={
        "ano": "anio",
        "nombrelocalidadresidencia": "nombre_localidad",
        "mesnotificacion": "mes",
        "trimestre": "trimestre",
        "casos": "casos",
        "tipoaseguramiento": "tipo_aseguramiento",
        "niveleducativo": "nivel_educativo",
        "orientsexual": "orientacion_sexual",
        "paisnacionalidad": "pais_nacionalidad",
        "curso_de_vida": "curso_de_vida",
    })
    return df


def normalize_tokens(df: pd.DataFrame) -> pd.DataFrame:
    # Unificar 'Sin dato' y similares a NA en variables categóricas
    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        s = df[col].astype(str).str.strip()
        mask = s.str.lower().isin(["sin dato", "sin  dato", "sindato", "n.a.", "n.a", "na", "n.a"]) | (s == "")
        df.loc[mask, col] = np.nan
    return df


def load_psicoactivas() -> pd.DataFrame:
    xls = pd.ExcelFile(RAW_XLSX, engine="openpyxl")
    # Usar la primera hoja por defecto (según inspección: 'Descargable_Vespa_Gral_050525')
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    return df


def main():
    ensure_dirs()

    print(f"Leyendo Excel: {RAW_XLSX}")
    df_raw = load_psicoactivas()

    # Exportación UTF-8 simple (CSV) para inspecciones rápidas
    print(f"Exportando UTF-8 sin transformar: {UTF8_EXPORT}")
    df_raw.to_csv(UTF8_EXPORT, index=False, encoding="utf-8")

    # Estandarizar columnas
    df = standardize_columns(df_raw)

    # Normalizar tokens 'sin dato'
    df = normalize_tokens(df)

    # Normalizar localidades
    if "nombre_localidad" in df.columns:
        df["nombre_localidad"] = df["nombre_localidad"].apply(normalize_localidad)

    # Tipos
    for col in ["anio", "mes", "trimestre", "casos"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Guardar versión limpia
    print(f"Exportando versión limpia: {CLEAN_EXPORT}")
    df.to_csv(CLEAN_EXPORT, index=False, encoding="utf-8")

    # Filtrar rango de estudio (2015–2024) para agregación principal
    df_agg = df.copy()
    if "anio" in df_agg.columns:
        df_agg = df_agg[(df_agg["anio"] >= 2015) & (df_agg["anio"] <= 2024)]

    # Excluir filas sin localidad o sin año antes de agregar
    excluded = 0
    if {"nombre_localidad", "anio"}.issubset(df_agg.columns):
        before = len(df_agg)
        df_agg = df_agg.dropna(subset=["nombre_localidad", "anio"]).copy()
        excluded = before - len(df_agg)

    # Agregación por localidad–año (sumar CASOS)
    if {"nombre_localidad", "anio", "casos"}.issubset(df_agg.columns):
        agg = (
            df_agg.groupby(["nombre_localidad", "anio"], dropna=False)["casos"]
            .sum(min_count=1)
            .reset_index()
            .rename(columns={"casos": "casos_consumo"})
        )
        print(f"Exportando agregación localidad–año: {AGG_EXPORT}")
        agg.to_csv(AGG_EXPORT, index=False, encoding="utf-8")
    else:
        print("Advertencia: columnas para agregación no encontradas. No se creó el archivo agregado.")
        agg = None

    # Reporte
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Reporte preparación Psicoactivas (VESPA)\n\n")
        f.write(f"Filas raw: {len(df_raw)}, Filas clean: {len(df)}\n\n")
        f.write("## Columnas (clean)\n\n")
        for c in df.columns:
            f.write(f"- {c}\n")
        if agg is not None:
            f.write("\n## Agregación\n\n")
            f.write(f"Filas agregadas: {len(agg)}\n")
            f.write(f"Filas excluidas por localidad/año faltantes: {excluded}\n")

    print("Listo. Revisa data/working/ y docs/prep_psicoactivas_report.md")


if __name__ == "__main__":
    main()
