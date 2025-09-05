import os
import pandas as pd
import numpy as np

from utils_localidad import normalize_localidad

CLEAN_INPUT = os.path.join("data", "working", "vintrafamiliar_clean.csv")
AGG_EXPORT = os.path.join("data", "working", "vif_localidad_anio.csv")
REPORT_PATH = os.path.join("docs", "aggregate_vif_report.md")


def ensure_dirs():
    os.makedirs(os.path.dirname(AGG_EXPORT), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def main():
    ensure_dirs()

    print(f"Leyendo limpio: {CLEAN_INPUT}")
    df = pd.read_csv(CLEAN_INPUT, dtype={"anio": "Int64"})

    # Normalizar localidades por seguridad
    if "nombre_localidad" in df.columns:
        df["nombre_localidad"] = df["nombre_localidad"].apply(normalize_localidad)

    # Asegurar tipo año
    if "anio" in df.columns:
        df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # Filtrar rango de estudio (2015–2024)
    df = df[(df["anio"] >= 2015) & (df["anio"] <= 2024)]

    # Agregación: conteo de registros como casos de víctimas
    if {"nombre_localidad", "anio"}.issubset(df.columns):
        agg = (
            df.groupby(["nombre_localidad", "anio"], dropna=False)
            .size()
            .reset_index(name="casos_violencia")
        )
        print(f"Exportando agregación VIF localidad–año: {AGG_EXPORT}")
        agg.to_csv(AGG_EXPORT, index=False, encoding="utf-8")
    else:
        raise ValueError("Faltan columnas requeridas 'nombre_localidad' y/o 'anio' en el input limpio.")

    # Reporte
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Reporte agregación Violencia (VIF)\n\n")
        f.write(f"Filas agregadas: {len(agg)}\n\n")
        f.write("## Primeras filas\n\n")
        f.write(agg.head(10).to_markdown(index=False))

    print("Listo. Revisa data/working/vif_localidad_anio.csv y docs/aggregate_vif_report.md")


if __name__ == "__main__":
    main()
