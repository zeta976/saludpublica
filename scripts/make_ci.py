import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

RATES_PATH = os.path.join("data", "working", "localidad_ano_master_rates.csv")
FIG_DIR = os.path.join("docs", "figs")
REPORT = os.path.join("docs", "ci_report.md")

CONF = 0.975  # >96% as requested
Z = 2.24      # approx z for 97.5% two-sided

sns.set(style="whitegrid", context="talk")


def ensure_dirs():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)


# Byar CI for Poisson count k
# lo ≈ k*(1 - 1/(9k) - z/(3*sqrt(k)))^3; hi ≈ (k+1)*(1 - 1/(9(k+1)) + z/(3*sqrt(k+1)))^3
# For k=0, use 0 for lower and -ln(alpha)/E for upper in rate space; here handle with small-k guard

def byar_ci_counts(k: np.ndarray, z: float) -> tuple[np.ndarray, np.ndarray]:
    k = np.asarray(k, dtype=float)
    lo = np.empty_like(k)
    hi = np.empty_like(k)
    for i, ki in enumerate(k):
        if ki <= 0:
            lo[i] = 0.0
            hi[i] = (1 - 1/(9*(ki+1)) + z/(3*math.sqrt(ki+1)))**3 * (ki+1)
        else:
            lo[i] = (1 - 1/(9*ki) - z/(3*math.sqrt(ki)))**3 * ki
            hi[i] = (1 - 1/(9*(ki+1)) + z/(3*math.sqrt(ki+1)))**3 * (ki+1)
    return lo, hi


def wilson_ci(k: int, n: int, z: float) -> tuple[float, float, float]:
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2/(2*n)) / denom
    half = z * math.sqrt((p*(1-p)/n) + (z**2/(4*n**2))) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def rate_ratio_ci(k_high: int, e_high: float, k_low: int, e_low: float, z: float) -> tuple[float, float, float]:
    # Poisson counts, exposures e; RR = (k_high/e_high)/(k_low/e_low)
    if k_high <= 0 or k_low <= 0 or e_high <= 0 or e_low <= 0:
        return (np.nan, np.nan, np.nan)
    rr = (k_high / e_high) / (k_low / e_low)
    se_log = math.sqrt(1/k_high + 1/k_low)
    lo = math.exp(math.log(rr) - z*se_log)
    hi = math.exp(math.log(rr) + z*se_log)
    return rr, lo, hi


def plot_bogota_rates_with_ci(df: pd.DataFrame):
    # aggregate by year for Bogotá totals
    out_rows = []
    for var_cases in ["casos_consumo", "casos_violencia"]:
        label = "Consumo" if var_cases=="casos_consumo" else "Violencia"
        g = df.groupby("anio", dropna=True).agg(
            k=(var_cases, "sum"),
            E=("poblacion", "sum")
        ).reset_index().dropna()
        lo_k, hi_k = byar_ci_counts(g["k"].to_numpy(), Z)
        rate = (g["k"] / g["E"]) * 100000
        lo = (lo_k / g["E"]) * 100000
        hi = (hi_k / g["E"]) * 100000

        # plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(g["anio"], rate, marker="o", color="#1f77b4" if var_cases=="casos_consumo" else "#d62728", label=f"{label}")
        ax.fill_between(g["anio"], lo, hi, alpha=0.25, color=ax.lines[0].get_color(), label=f"IC {int(CONF*100)}%")
        ax.set_title(f"Bogotá: {label} — tasa por 100.000 con IC {int(CONF*100)}% (Byar)")
        ax.set_xlabel("Año")
        ax.set_ylabel("Tasa por 100.000 hab.")
        ax.legend()
        fname = f"bogota_tasas_ic_{'consumo' if var_cases=='casos_consumo' else 'violencia'}.png"
        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, fname), dpi=200)
        plt.close()
        print(f"Guardado: {os.path.join(FIG_DIR, fname)}")
        for a, r, l, h in zip(g["anio"], rate, lo, hi):
            out_rows.append({"variable": label, "anio": int(a), "rate": float(r), "lo": float(l), "hi": float(h)})

    return pd.DataFrame(out_rows)


def plot_wilson_two_periods(df: pd.DataFrame):
    # Success = tasa_violencia > tasa_consumo at localidad-year level
    df = df.dropna(subset=["tasa_consumo_100k", "tasa_violencia_100k"]).copy()
    df["periodo"] = np.where(df["anio"] <= 2019, "2015–2019", "2020–2024")
    tbl = []
    for periodo, sub in df.groupby("periodo"):
        n = len(sub)
        k = int((sub["tasa_violencia_100k"] > sub["tasa_consumo_100k"]).sum())
        p, lo, hi = wilson_ci(k, n, Z)
        tbl.append({"periodo": periodo, "k": k, "n": n, "p": p, "lo": lo, "hi": hi})
    res = pd.DataFrame(tbl)

    # plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(res["p"], res["periodo"], xerr=[res["p"]-res["lo"], res["hi"]-res["p"]], fmt="o", color="#333")
    ax.set_xlabel("Proporción (VIF > Consumo)")
    ax.set_ylabel("")
    ax.set_title(f"Proporción con IC {int(CONF*100)}% (Wilson)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "prop_vif_mayor_consumo_wilson.png"), dpi=200)
    plt.close()
    print(f"Guardado: {os.path.join(FIG_DIR, 'prop_vif_mayor_consumo_wilson.png')}")

    return res


def plot_rate_ratio_forest(df: pd.DataFrame):
    # Categorize by consumption rate quartiles per year to mitigate confounding by year level changes
    df = df.dropna(subset=["tasa_consumo_100k", "casos_violencia", "poblacion"]).copy()
    # Quartiles by year
    df["q_consumo"] = df.groupby("anio")["tasa_consumo_100k"].transform(lambda s: pd.qcut(s.rank(method='first'), 4, labels=[1,2,3,4]))
    high = df[df["q_consumo"].astype(int) == 4]
    low = df[df["q_consumo"].astype(int) == 1]

    k_high = int(high["casos_violencia"].sum())
    e_high = float(high["poblacion"].sum())
    k_low = int(low["casos_violencia"].sum())
    e_low = float(low["poblacion"].sum())
    rr, lo, hi = rate_ratio_ci(k_high, e_high, k_low, e_low, Z)

    # forest-like single point
    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.errorbar(rr, 0, xerr=[[rr-lo], [hi-rr]], fmt="o", color="#2ca02c")
    ax.axvline(1.0, color="k", lw=1)
    ax.set_yticks([])
    ax.set_xlabel("Razón de tasas de violencia (alto vs bajo consumo)")
    ax.set_title(f"RR con IC {int(CONF*100)}% — estratificado por año (Q4 vs Q1)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "rr_violencia_alto_vs_bajo_consumo.png"), dpi=200)
    plt.close()
    print(f"Guardado: {os.path.join(FIG_DIR, 'rr_violencia_alto_vs_bajo_consumo.png')}")

    return {
        "k_low": k_low, "e_low": e_low,
        "k_high": k_high, "e_high": e_high,
        "rr": rr, "lo": lo, "hi": hi,
    }


def main():
    ensure_dirs()
    if not os.path.exists(RATES_PATH):
        raise FileNotFoundError(f"No existe {RATES_PATH}. Corre compute_rates.py")

    df = pd.read_csv(RATES_PATH, dtype={"anio": "Int64"})

    # 1) Bogotá rates with Byar CI
    bog = plot_bogota_rates_with_ci(df)

    # 2) Wilson for proportion VIF>Consumo by two periods
    wil = plot_wilson_two_periods(df)

    # 3) Rate ratio high vs low consumption
    rr = plot_rate_ratio_forest(df)

    # Write report with tables
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(f"# Intervalos de confianza para indicadores clave (IC {int(CONF*100)}%)\n\n")
        f.write("Este reporte utiliza métodos apropiados para conteos de eventos poco frecuentes y proporciones:\n\n")
        f.write("- Tasas por 100.000: IC de Byar (aprox. Poisson) para agregados de Bogotá por año.\n")
        f.write("- Proporciones: IC de Wilson para la fracción de celdas localidad–año con VIF > Consumo, comparando 2015–2019 vs 2020–2024.\n")
        f.write("- Razón de tasas (RR): IC log-normal para comparar violencia entre celdas con consumo alto (Q4) vs bajo (Q1).\n\n")

        f.write("## 1) Bogotá: tasas con IC (Byar)\n\n")
        f.write("Se muestran dos figuras: consumo y violencia, cada una con su banda de IC.\n\n")
        f.write("Archivos: docs/figs/bogota_tasas_ic_consumo.png y docs/figs/bogota_tasas_ic_violencia.png\n\n")

        f.write("## 2) Proporción (Wilson) — VIF > Consumo\n\n")
        f.write(wil.to_markdown(index=False))
        f.write("\n\nArchivo: docs/figs/prop_vif_mayor_consumo_wilson.png\n\n")
        f.write("Interpretación: el porcentaje estimado indica la fracción de combinaciones localidad–año donde la tasa de violencia supera a la de consumo. El intervalo de confianza ")
        f.write(f"{int(CONF*100)}% refleja la incertidumbre debida al tamaño de muestra.\n\n")

        f.write("## 3) Razón de tasas de violencia (alto vs bajo consumo)\n\n")
        f.write(pd.DataFrame([rr]).to_markdown(index=False))
        f.write("\n\nArchivo: docs/figs/rr_violencia_alto_vs_bajo_consumo.png\n\n")
        f.write("Interpretación: RR>1 sugiere mayor riesgo de violencia en las celdas con tasas de consumo en el cuartil superior respecto al cuartil inferior, tras ajustar por población mediante tasas. ")
        f.write("El IC indica el rango compatible con los datos; si incluye 1, la evidencia no es concluyente para una diferencia.\n")

    print(f"Reporte generado: {REPORT}")


if __name__ == "__main__":
    main()
