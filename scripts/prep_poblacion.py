import os
import pandas as pd
import numpy as np

from utils_localidad import normalize_localidad

RAW_POB = os.path.join("data", "raw", "poblacion.xlsx")
OUT_CSV = os.path.join("data", "working", "poblacion_localidad_anio.csv")
REPORT = os.path.join("docs", "prep_poblacion_report.md")


def ensure_dirs():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Intentar mapear columnas típicas observadas: COD_LOC, NOM_LOC, AREA, AÑO, Total Hombre, Total Mujeres, TOTAL
    cols = {c.lower().strip(): c for c in df.columns}
    # Buscar candidatos por inclusión de palabras clave
    def find(col_keys):
        for k, orig in cols.items():
            if any(key in k for key in col_keys):
                return orig
        return None

    col_nom = find(["nom_loc", "localidad", "nomloc", "nombre"])
    col_anio = find(["año", "ano", "anio", "year"])
    col_total = find(["total", "poblacion", "población"])

    if col_nom is None or col_anio is None or col_total is None:
        raise ValueError(
            f"No se pudieron identificar columnas clave en poblacion.xlsx. Encontradas: {list(df.columns)}"
        )

    out = df[[col_nom, col_anio, col_total]].copy()
    out.columns = ["nombre_localidad", "anio", "poblacion"]
    return out


def load_poblacion() -> pd.DataFrame:
    # Leer todas las hojas si existen y concatenar
    xls = pd.ExcelFile(RAW_POB, engine="openpyxl")
    frames = []
    for sh in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sh)
        except Exception:
            continue
        frames.append(df)
    if not frames:
        raise FileNotFoundError("No se pudo leer ninguna hoja de poblacion.xlsx")
    df = pd.concat(frames, ignore_index=True)
    return df


def expand_years(pob: pd.DataFrame) -> pd.DataFrame:
    # Normalizar localidad y tipos
    pob["nombre_localidad"] = pob["nombre_localidad"].apply(normalize_localidad)
    pob = pob.dropna(subset=["nombre_localidad"]).copy()

    pob["anio"] = pd.to_numeric(pob["anio"], errors="coerce").astype("Int64")
    pob["poblacion"] = pd.to_numeric(pob["poblacion"], errors="coerce")

    # Mantener solo años válidos y colapsar por suma si vienen duplicados
    pob = (
        pob.dropna(subset=["anio"]) \
           .groupby(["nombre_localidad", "anio"], as_index=False)["poblacion"].sum()
    )

    # Rango objetivo 2015–2024. Para años < 2018 asumir población de 2018.
    target_years = list(range(2015, 2025))

    # Obtener valor 2018 por localidad
    base2018 = pob[pob["anio"] == 2018][["nombre_localidad", "poblacion"]].rename(columns={"poblacion": "pob2018"})

    # Expandir grilla completa
    localidades = sorted(pob["nombre_localidad"].unique().tolist())
    grid = pd.MultiIndex.from_product([localidades, target_years], names=["nombre_localidad", "anio"]).to_frame(index=False)

    merged = grid.merge(pob, on=["nombre_localidad", "anio"], how="left")
    merged = merged.merge(base2018, on="nombre_localidad", how="left")

    # Relleno: si año < 2018 y falta población, usar pob2018. Sino dejar NA si tampoco hay base.
    cond_fill = (merged["anio"] < 2018) & merged["poblacion"].isna()
    merged.loc[cond_fill, "poblacion"] = merged.loc[cond_fill, "pob2018"]

    merged = merged.drop(columns=["pob2018"]) \
                   .sort_values(["nombre_localidad", "anio"]) \
                   .reset_index(drop=True)
    return merged


def main():
    ensure_dirs()

    if not os.path.exists(RAW_POB):
        raise FileNotFoundError(f"No existe {RAW_POB}")

    raw = load_poblacion()
    std = _standardize_columns(raw)
    expanded = expand_years(std)

    expanded.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # Reporte
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Preparación de población por localidad–año\n\n")
        f.write(f"Filas originales: {len(raw)}\n\n")
        f.write(f"Filas estandarizadas: {len(std)}\n\n")
        f.write(f"Filas en grilla 2015–2024: {len(expanded)}\n\n")
        f.write("## Ejemplo (primeras 20 filas)\n\n")
        f.write(expanded.head(20).to_markdown(index=False))
        f.write("\n")

    print(f"Población preparada: {OUT_CSV}")
    print(f"Reporte: {REPORT}")


if __name__ == "__main__":
    main()
