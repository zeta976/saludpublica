import os
import pandas as pd

from utils_localidad import normalize_localidad

PSICO_PATH = os.path.join("data", "working", "psicoactivas_localidad_anio.csv")
VIF_PATH = os.path.join("data", "working", "vif_localidad_anio.csv")
OUT_PATH = os.path.join("data", "working", "localidad_ano_master.csv")
REPORT_PATH = os.path.join("docs", "join_master_report.md")


def ensure_dirs():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def main():
    ensure_dirs()

    psico = pd.read_csv(PSICO_PATH, dtype={"anio": "Int64"}) if os.path.exists(PSICO_PATH) else None
    vif = pd.read_csv(VIF_PATH, dtype={"anio": "Int64"}) if os.path.exists(VIF_PATH) else None

    if psico is None or vif is None:
        missing = [p for p, ok in [(PSICO_PATH, psico is not None), (VIF_PATH, vif is not None)] if not ok]
        raise FileNotFoundError(f"Faltan insumos para el join: {missing}")

    # Normalizar localidades y depurar claves nulas como salvaguarda final
    if "nombre_localidad" in psico.columns:
        psico["nombre_localidad"] = psico["nombre_localidad"].apply(normalize_localidad)
    if "nombre_localidad" in vif.columns:
        vif["nombre_localidad"] = vif["nombre_localidad"].apply(normalize_localidad)

    # Tipos año
    for df in (psico, vif):
        if "anio" in df.columns:
            df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # Contar y descartar claves con NA
    psico_before = len(psico)
    vif_before = len(vif)
    psico = psico.dropna(subset=["nombre_localidad", "anio"]).copy()
    vif = vif.dropna(subset=["nombre_localidad", "anio"]).copy()
    psico_dropped = psico_before - len(psico)
    vif_dropped = vif_before - len(vif)

    # Outer join para no perder localidades con ceros en una u otra fuente
    master = pd.merge(
        psico,
        vif,
        on=["nombre_localidad", "anio"],
        how="outer",
        validate="one_to_one",
    )

    # Flags de presencia
    master["en_psicoactivas"] = master["casos_consumo"].notna()
    master["en_vif"] = master["casos_violencia"].notna()

    # Completar con 0 donde falte conteo
    master["casos_consumo"] = master["casos_consumo"].fillna(0).astype("Int64")
    master["casos_violencia"] = master["casos_violencia"].fillna(0).astype("Int64")

    # Ordenar columnas
    cols = ["nombre_localidad", "anio", "casos_consumo", "casos_violencia", "en_psicoactivas", "en_vif"]
    other_cols = [c for c in master.columns if c not in cols]
    master = master[cols + other_cols]

    # Exportar
    master.to_csv(OUT_PATH, index=False, encoding="utf-8")

    # Reporte
    only_psico = master[master["en_psicoactivas"] & (~master["en_vif"])][["nombre_localidad", "anio"]]
    only_vif = master[(~master["en_psicoactivas"]) & master["en_vif"]][["nombre_localidad", "anio"]]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Reporte unión localidad–año\n\n")
        f.write(f"Filas master: {len(master)}\n\n")
        f.write(f"Registros descartados por claves nulas: psico={psico_dropped}, vif={vif_dropped}\n\n")
        f.write("## Registros solo en psicoactivas (no en VIF)\n\n")
        if not only_psico.empty:
            f.write(only_psico.head(50).to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("(Ninguno)\n\n")
        f.write("## Registros solo en VIF (no en psicoactivas)\n\n")
        if not only_vif.empty:
            f.write(only_vif.head(50).to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("(Ninguno)\n\n")

    print(f"Master exportado: {OUT_PATH}")
    print(f"Reporte: {REPORT_PATH}")


if __name__ == "__main__":
    main()
