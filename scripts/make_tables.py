import os
import pandas as pd

MASTER_PATH = os.path.join("data", "working", "localidad_ano_master.csv")
OUT_DIR_DATA = os.path.join("data", "working")
OUT_DIR_DOCS = os.path.join("docs")

GLOBAL_MD = os.path.join(OUT_DIR_DOCS, "descriptivos_globales.md")
LOC_MD = os.path.join(OUT_DIR_DOCS, "tablas_localidad_resumen.md")
ANIO_MD = os.path.join(OUT_DIR_DOCS, "tablas_anuales_bogota.md")

MATRIZ_CONSUMO = os.path.join(OUT_DIR_DATA, "matriz_casos_consumo.csv")
MATRIZ_VIOLENCIA = os.path.join(OUT_DIR_DATA, "matriz_casos_violencia.csv")


def ensure_dirs():
    os.makedirs(OUT_DIR_DATA, exist_ok=True)
    os.makedirs(OUT_DIR_DOCS, exist_ok=True)


def main():
    ensure_dirs()
    if not os.path.exists(MASTER_PATH):
        raise FileNotFoundError(f"No existe {MASTER_PATH}. Corre primero join_master.py")

    df = pd.read_csv(MASTER_PATH, dtype={"anio": "Int64"})

    # --- Resumen global 2015–2024 ---
    total_consumo = int(df["casos_consumo"].sum())
    total_violencia = int(df["casos_violencia"].sum())
    corr = df[["casos_consumo", "casos_violencia"]].corr().iloc[0, 1]

    with open(GLOBAL_MD, "w", encoding="utf-8") as f:
        f.write("# Descriptivos globales (2015–2024)\n\n")
        f.write(f"- Total casos consumo (suma localidades×años): {total_consumo}\n")
        f.write(f"- Total casos violencia (suma localidades×años): {total_violencia}\n")
        f.write(f"- Correlación Pearson entre casos consumo y violencia (por clave localidad–año): {corr:.3f}\n")

    # --- Resumen por localidad (suma 2015–2024) ---
    loc_sum = (
        df.groupby("nombre_localidad", dropna=False)[["casos_consumo", "casos_violencia"]]
          .sum()
          .sort_values("casos_consumo", ascending=False)
    )

    top10_consumo = loc_sum.sort_values("casos_consumo", ascending=False).head(10)
    top10_violencia = loc_sum.sort_values("casos_violencia", ascending=False).head(10)

    with open(LOC_MD, "w", encoding="utf-8") as f:
        f.write("# Resumen por localidad (suma 2015–2024)\n\n")
        f.write("## Tabla completa (ordenada por casos_consumo)\n\n")
        f.write(loc_sum.to_markdown())
        f.write("\n\n## Top 10 por consumo\n\n")
        f.write(top10_consumo.to_markdown())
        f.write("\n\n## Top 10 por violencia\n\n")
        f.write(top10_violencia.to_markdown())
        f.write("\n")

    # --- Resumen por año (Bogotá total) ---
    anio_sum = (
        df.groupby("anio")[["casos_consumo", "casos_violencia"]]
          .sum()
          .sort_index()
    )

    with open(ANIO_MD, "w", encoding="utf-8") as f:
        f.write("# Totales por año (Bogotá)\n\n")
        f.write(anio_sum.to_markdown())
        f.write("\n")

    # --- Matrices pivote año×localidad para heatmaps ---
    pivot_consumo = df.pivot_table(index="anio", columns="nombre_localidad", values="casos_consumo", aggfunc="sum")
    pivot_violencia = df.pivot_table(index="anio", columns="nombre_localidad", values="casos_violencia", aggfunc="sum")
    pivot_consumo.to_csv(MATRIZ_CONSUMO, encoding="utf-8")
    pivot_violencia.to_csv(MATRIZ_VIOLENCIA, encoding="utf-8")

    print("Tablas generadas:")
    print(f" - {GLOBAL_MD}")
    print(f" - {LOC_MD}")
    print(f" - {ANIO_MD}")
    print("Matrices pivote:")
    print(f" - {MATRIZ_CONSUMO}")
    print(f" - {MATRIZ_VIOLENCIA}")


if __name__ == "__main__":
    main()
