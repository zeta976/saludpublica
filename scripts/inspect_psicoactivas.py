import os
import pandas as pd

RAW_XLSX = os.path.join("data", "raw", "psicoactivas.xlsx")
REPORT = os.path.join("docs", "psicoactivas_inspect.md")


def main():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)

    # Listar hojas
    try:
        xls = pd.ExcelFile(RAW_XLSX, engine="openpyxl")
    except Exception as e:
        print(f"Error abriendo {RAW_XLSX}: {e}")
        return

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Inspección inicial psicoactivas.xlsx\n\n")
        f.write(f"Archivo: {RAW_XLSX}\n\n")
        f.write("## Hojas disponibles\n\n")
        for name in xls.sheet_names:
            f.write(f"- {name}\n")
        f.write("\n## Columnas por hoja (primeras 5 filas de ejemplo)\n\n")

        for name in xls.sheet_names:
            f.write(f"### Hoja: {name}\n\n")
            try:
                df = pd.read_excel(xls, sheet_name=name, nrows=5)
            except Exception as e:
                f.write(f"No se pudo leer la hoja: {e}\n\n")
                continue
            f.write("Columnas:\n")
            for c in df.columns:
                f.write(f"- {c}\n")
            f.write("\nMuestra (5 filas):\n\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n")

    print(f"Reporte generado: {REPORT}")


if __name__ == "__main__":
    main()
