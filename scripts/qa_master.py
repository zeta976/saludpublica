import os
import pandas as pd

MASTER_PATH = os.path.join("data", "working", "localidad_ano_master.csv")
REPORT_PATH = os.path.join("docs", "qa_master_report.md")


def ensure_dirs():
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def main():
    ensure_dirs()
    if not os.path.exists(MASTER_PATH):
        raise FileNotFoundError(f"No existe {MASTER_PATH}. Corre primero join_master.py")

    df = pd.read_csv(MASTER_PATH, dtype={"anio": "Int64"})

    # Resumen general
    n_rows, n_cols = df.shape
    missing_by_col = df.isna().sum().sort_values(ascending=False)

    # Zeros por fuente
    zeros_consumo = (df["casos_consumo"] == 0).sum()
    zeros_violencia = (df["casos_violencia"] == 0).sum()

    # Correlación preliminar casos (no tasas aún)
    corr = df[["casos_consumo", "casos_violencia"]].corr().iloc[0, 1]

    # Localidades con mayores casos
    top_consumo = (
        df.groupby("nombre_localidad")["casos_consumo"].sum().sort_values(ascending=False).head(10)
    )
    top_violencia = (
        df.groupby("nombre_localidad")["casos_violencia"].sum().sort_values(ascending=False).head(10)
    )

    # Años cubiertos por localidad
    cobertura = (
        df.groupby("nombre_localidad")["anio"].nunique().sort_values(ascending=True)
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# QA tabla maestra (localidad–año)\n\n")
        f.write(f"Filas: {n_rows}, Columnas: {n_cols}\n\n")
        f.write("## Missing por columna (top 10)\n\n")
        f.write(missing_by_col.head(10).to_markdown())
        f.write("\n\n")
        f.write("## Conteos en cero\n\n")
        f.write(f"casos_consumo == 0: {zeros_consumo}\n\n")
        f.write(f"casos_violencia == 0: {zeros_violencia}\n\n")
        f.write("## Correlación preliminar entre casos (no ajustado por población)\n\n")
        f.write(f"corr(casos_consumo, casos_violencia) = {corr:.3f}\n\n")
        f.write("## Localidades con mayor consumo (suma 2015–2024)\n\n")
        f.write(top_consumo.to_markdown())
        f.write("\n\n")
        f.write("## Localidades con mayor violencia (suma 2015–2024)\n\n")
        f.write(top_violencia.to_markdown())
        f.write("\n\n")
        f.write("## Cobertura de años por localidad (número de años)\n\n")
        f.write(cobertura.to_markdown())
        f.write("\n")

    print(f"Reporte QA generado: {REPORT_PATH}")


if __name__ == "__main__":
    main()
