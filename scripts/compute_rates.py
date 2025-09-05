import os
import pandas as pd

from utils_localidad import normalize_localidad

MASTER_IN = os.path.join("data", "working", "localidad_ano_master.csv")
POB_PATH = os.path.join("data", "working", "poblacion_localidad_anio.csv")
MASTER_OUT = os.path.join("data", "working", "localidad_ano_master_rates.csv")
REPORT_PATH = os.path.join("docs", "rates_report.md")


def ensure_dirs():
    os.makedirs(os.path.dirname(MASTER_OUT), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def main():
    ensure_dirs()

    if not os.path.exists(MASTER_IN):
        raise FileNotFoundError(f"No existe {MASTER_IN}. Corre primero join_master.py")
    if not os.path.exists(POB_PATH):
        # Plantilla para que el usuario la llene
        tpl = pd.DataFrame({
            "nombre_localidad": [
                "usaquén","chapinero","santa fe","san cristóbal","usme","tunjuelito",
                "bosa","kennedy","fontibón","engativá","suba","barrios unidos",
                "teusaquillo","los mártires","antonio nariño","puente aranda","la candelaria",
                "rafael uribe uribe","ciudad bolívar","sumapaz"
            ],
            "anio": [2015]*20,
            "poblacion": [None]*20,
        })
        tpl.to_csv(POB_PATH, index=False, encoding="utf-8")
        raise FileNotFoundError(
            f"No existe {POB_PATH}. He creado una plantilla. Llénala con columnas: nombre_localidad, anio, poblacion"
        )

    df = pd.read_csv(MASTER_IN, dtype={"anio": "Int64"})
    pob = pd.read_csv(POB_PATH, dtype={"anio": "Int64"})

    # Normalizar localidades en población y master por seguridad
    pob["nombre_localidad"] = pob["nombre_localidad"].apply(normalize_localidad)
    df["nombre_localidad"] = df["nombre_localidad"].apply(normalize_localidad)

    # Merge left para mantener todas las claves del master
    merged = df.merge(
        pob, on=["nombre_localidad", "anio"], how="left", validate="m:1"
    )

    # Calcular tasas por 100.000 si hay población
    merged["poblacion"] = pd.to_numeric(merged["poblacion"], errors="coerce")
    merged["poblacion_baja"] = merged["poblacion"].fillna(0) < 1000

    def safe_rate(num, den):
        if pd.isna(den) or den <= 0:
            return pd.NA
        return (num / den) * 100000

    merged["tasa_consumo_100k"] = [
        safe_rate(n, d) for n, d in zip(merged["casos_consumo"], merged["poblacion"])
    ]
    merged["tasa_violencia_100k"] = [
        safe_rate(n, d) for n, d in zip(merged["casos_violencia"], merged["poblacion"])
    ]

    # Exportar
    merged.to_csv(MASTER_OUT, index=False, encoding="utf-8")

    # Reporte
    miss_pob = merged["poblacion"].isna().sum()
    total = len(merged)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Reporte de tasas (por 100.000)\n\n")
        f.write(f"Filas: {total}\n\n")
        f.write(f"Registros sin población: {miss_pob} ({miss_pob/total:.1%})\n\n")
        f.write("## Ejemplo (primeras 10 filas)\n\n")
        f.write(merged.head(10).to_markdown(index=False))
        f.write("\n")

    print(f"Guardado: {MASTER_OUT}")
    print(f"Reporte: {REPORT_PATH}")


if __name__ == "__main__":
    main()
