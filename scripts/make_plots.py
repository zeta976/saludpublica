import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

MASTER_PATH = os.path.join("data", "working", "localidad_ano_master.csv")
MASTER_RATES_PATH = os.path.join("data", "working", "localidad_ano_master_rates.csv")
FIG_DIR = os.path.join("docs", "figs")

sns.set(style="whitegrid", context="talk")


def ensure_dirs():
    os.makedirs(FIG_DIR, exist_ok=True)


def savefig(path: str):
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Guardado: {path}")


def plot_series_bogota(df: pd.DataFrame):
    anio_sum = df.groupby("anio")[ ["casos_consumo", "casos_violencia" ] ].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(anio_sum["anio"], anio_sum["casos_consumo"], marker="o", label="Consumo (casos)")
    ax.plot(anio_sum["anio"], anio_sum["casos_violencia"], marker="o", label="Violencia (casos)")
    ax.set_title("Bogotá: series de tiempo de casos (2015–2024)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Casos")
    ax.legend()
    savefig(os.path.join(FIG_DIR, "lineas_bogota_casos.png"))


def plot_top_bars(df: pd.DataFrame):
    loc_sum = df.groupby("nombre_localidad")[ ["casos_consumo", "casos_violencia" ] ].sum().reset_index()
    for var, title in [("casos_consumo", "Top 10 localidades por consumo (casos, 2015–2024)"),
                       ("casos_violencia", "Top 10 localidades por violencia (casos, 2015–2024)")]:
        top = loc_sum.sort_values(var, ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=top, y="nombre_localidad", x=var, ax=ax, palette="viridis")
        ax.set_title(title)
        ax.set_xlabel("Casos")
        ax.set_ylabel("")
        fname = f"top10_{var}.png"
        savefig(os.path.join(FIG_DIR, fname))


def plot_heatmaps(df: pd.DataFrame):
    for var in ["casos_consumo", "casos_violencia"]:
        pivot = df.pivot_table(index="anio", columns="nombre_localidad", values=var, aggfunc="sum")
        # ordenar columnas por suma total descendente para legibilidad
        order = pivot.sum(axis=0).sort_values(ascending=False).index
        pivot = pivot[order]
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(pivot, cmap="magma", ax=ax)
        ax.set_title(f"Heatmap año×localidad de {var}")
        ax.set_xlabel("Localidad")
        ax.set_ylabel("Año")
        savefig(os.path.join(FIG_DIR, f"heatmap_{var}.png"))


def plot_scatter(df: pd.DataFrame):
    # Scatter por clave localidad–año con línea de tendencia
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=df, x="casos_consumo", y="casos_violencia", scatter_kws={"alpha": 0.6}, line_kws={"color": "red"}, ax=ax)
    ax.set_title("Relación casos de consumo vs violencia (localidad–año)")
    ax.set_xlabel("Casos de consumo")
    ax.set_ylabel("Casos de violencia")
    savefig(os.path.join(FIG_DIR, "scatter_consumo_vs_violencia.png"))


# ----------------------
# Gráficas ajustadas por población (tasas por 100.000)
# ----------------------

def has_rates(df: pd.DataFrame) -> bool:
    return {"tasa_consumo_100k", "tasa_violencia_100k"}.issubset(df.columns)


def plot_series_bogota_rates(df: pd.DataFrame):
    anio_mean = df.groupby("anio")[ ["tasa_consumo_100k", "tasa_violencia_100k" ] ].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(anio_mean["anio"], anio_mean["tasa_consumo_100k"], marker="o", label="Consumo (tasa por 100.000)")
    ax.plot(anio_mean["anio"], anio_mean["tasa_violencia_100k"], marker="o", label="Violencia (tasa por 100.000)")
    ax.set_title("Bogotá: series de tiempo de tasas (2015–2024)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Tasa por 100.000 hab.")
    ax.legend()
    savefig(os.path.join(FIG_DIR, "lineas_bogota_tasas.png"))


def plot_heatmaps_rates(df: pd.DataFrame):
    for var in ["tasa_consumo_100k", "tasa_violencia_100k"]:
        pivot = df.pivot_table(index="anio", columns="nombre_localidad", values=var, aggfunc="mean")
        order = pivot.mean(axis=0).sort_values(ascending=False).index
        pivot = pivot[order]
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(pivot, cmap="crest", ax=ax)
        ax.set_title(f"Heatmap año×localidad de {var} (promedio)")
        ax.set_xlabel("Localidad")
        ax.set_ylabel("Año")
        cbar = ax.collections[0].colorbar
        cbar.set_label("Tasa por 100.000 hab.")
        savefig(os.path.join(FIG_DIR, f"heatmap_{var}.png"))


def plot_facets_rates(df: pd.DataFrame):
    # Pequeños múltiplos por localidad para ver trayectorias
    g = sns.FacetGrid(df, col="nombre_localidad", col_wrap=5, height=2.2, sharey=False)
    g.map_dataframe(sns.lineplot, x="anio", y="tasa_consumo_100k", marker="o", color="#1f77b4")
    g.set_titles(col_template="{col_name}")
    g.set_axis_labels("Año", "Tasa por 100.000")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Trayectorias de tasa de consumo por localidad")
    savefig(os.path.join(FIG_DIR, "facets_tasa_consumo.png"))

    g = sns.FacetGrid(df, col="nombre_localidad", col_wrap=5, height=2.2, sharey=False)
    g.map_dataframe(sns.lineplot, x="anio", y="tasa_violencia_100k", marker="o", color="#d62728")
    g.set_titles(col_template="{col_name}")
    g.set_axis_labels("Año", "Tasa por 100.000")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Trayectorias de tasa de violencia por localidad")
    savefig(os.path.join(FIG_DIR, "facets_tasa_violencia.png"))


def plot_scatter_rates(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=df, x="tasa_consumo_100k", y="tasa_violencia_100k",
        scatter_kws={"alpha": 0.5}, line_kws={"color": "red"}, ax=ax
    )
    # Calcular r de Pearson global
    sub = df[["tasa_consumo_100k", "tasa_violencia_100k"]].dropna()
    if len(sub) >= 2:
        r = sub.corr(method="pearson").iloc[0, 1]
        ax.text(0.02, 0.98, f"r = {r:.2f}", transform=ax.transAxes, va="top", ha="left",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))
    ax.set_title("Relación tasas de consumo vs violencia (localidad–año)")
    ax.set_xlabel("Tasa de consumo (por 100.000)")
    ax.set_ylabel("Tasa de violencia (por 100.000)")
    savefig(os.path.join(FIG_DIR, "scatter_tasas_consumo_vs_violencia.png"))


def plot_hexbin_rates(df: pd.DataFrame):
    # Densidad bivariada para ver estructura no lineal y colas
    fig, ax = plt.subplots(figsize=(7.5, 6))
    hb = ax.hexbin(df["tasa_consumo_100k"], df["tasa_violencia_100k"], gridsize=30, cmap="viridis", mincnt=1)
    ax.set_xlabel("Tasa de consumo (por 100.000)")
    ax.set_ylabel("Tasa de violencia (por 100.000)")
    ax.set_title("Densidad bivariada de tasas")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label("N° de celdas")
    savefig(os.path.join(FIG_DIR, "hexbin_tasas.png"))


def plot_corr_by_localidad(df: pd.DataFrame):
    # Correlación por localidad (Pearson) usando tasas
    rs = (
        df.dropna(subset=["tasa_consumo_100k", "tasa_violencia_100k"]) \
          .groupby("nombre_localidad")[["tasa_consumo_100k", "tasa_violencia_100k"]] \
          .corr(method="pearson")
    )
    # El resultado es un MultiIndex. Extraer r entre las dos series
    rloc = rs.reset_index()
    rloc = rloc[(rloc["level_1"] == "tasa_violencia_100k") & (rloc["tasa_consumo_100k"].notna())]
    rloc = rloc[["nombre_localidad", "tasa_consumo_100k"]].rename(columns={"tasa_consumo_100k": "r"})
    rloc = rloc.sort_values("r", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(data=rloc, y="nombre_localidad", x="r", ax=ax, palette="coolwarm", hue=None)
    ax.set_title("Correlación (r de Pearson) entre tasas por localidad")
    ax.set_xlabel("r (consumo vs violencia)")
    ax.set_ylabel("")
    ax.axvline(0, color="k", linewidth=1)
    savefig(os.path.join(FIG_DIR, "correlacion_por_localidad_tasas.png"))


def plot_lagged_relationship(df: pd.DataFrame):
    # Explorar si la tasa de consumo en t se asocia con la tasa de violencia en t+1 (dentro de localidad)
    df_lag = df.sort_values(["nombre_localidad", "anio"]).copy()
    df_lag["tasa_violencia_100k_lag1"] = df_lag.groupby("nombre_localidad")["tasa_violencia_100k"].shift(-1)
    sub = df_lag.dropna(subset=["tasa_consumo_100k", "tasa_violencia_100k_lag1"]) \
                 [["tasa_consumo_100k", "tasa_violencia_100k_lag1"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=sub, x="tasa_consumo_100k", y="tasa_violencia_100k_lag1",
                scatter_kws={"alpha": 0.4}, line_kws={"color": "red"}, ax=ax)
    if len(sub) >= 2:
        r = sub.corr(method="pearson").iloc[0, 1]
        ax.text(0.02, 0.98, f"r = {r:.2f}", transform=ax.transAxes, va="top", ha="left",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))
    ax.set_title("Tasa consumo (t) vs Tasa violencia (t+1) — todas las localidades")
    ax.set_xlabel("Tasa de consumo en t (por 100.000)")
    ax.set_ylabel("Tasa de violencia en t+1 (por 100.000)")
    savefig(os.path.join(FIG_DIR, "lag1_scatter_tasas.png"))


def main():
    ensure_dirs()
    if not os.path.exists(MASTER_PATH):
        raise FileNotFoundError(f"No existe {MASTER_PATH}. Corre primero join_master.py")

    # Cargar master y, si existe, archivo con tasas
    df_master = pd.read_csv(MASTER_PATH, dtype={"anio": "Int64"})

    # Intentar cargar archivo de tasas (compute_rates.py)
    if os.path.exists(MASTER_RATES_PATH):
        df_rates = pd.read_csv(MASTER_RATES_PATH, dtype={"anio": "Int64"})
    else:
        df_rates = None

    # Gráficas en conteos (para referencia)
    plot_series_bogota(df_master)
    plot_top_bars(df_master)
    plot_heatmaps(df_master)
    plot_scatter(df_master)

    # Gráficas ajustadas por población si hay tasas
    if df_rates is not None and has_rates(df_rates):
        plot_series_bogota_rates(df_rates)
        plot_heatmaps_rates(df_rates)
        plot_facets_rates(df_rates)
        plot_scatter_rates(df_rates)
        plot_hexbin_rates(df_rates)
        plot_corr_by_localidad(df_rates)
        plot_lagged_relationship(df_rates)
    else:
        print("Advertencia: no se encontró archivo de tasas. Ejecuta scripts: prep_poblacion.py y compute_rates.py")

    print("Figuras generadas en docs/figs/")


if __name__ == "__main__":
    main()
