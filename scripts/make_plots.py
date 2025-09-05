import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

MASTER_PATH = os.path.join("data", "working", "localidad_ano_master.csv")
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
    anio_sum = df.groupby("anio")[ ["casos_consumo", "casos_violencia"] ].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(anio_sum["anio"], anio_sum["casos_consumo"], marker="o", label="Consumo (casos)")
    ax.plot(anio_sum["anio"], anio_sum["casos_violencia"], marker="o", label="Violencia (casos)")
    ax.set_title("Bogotá: series de tiempo de casos (2015–2024)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Casos")
    ax.legend()
    savefig(os.path.join(FIG_DIR, "lineas_bogota_casos.png"))


def plot_top_bars(df: pd.DataFrame):
    loc_sum = df.groupby("nombre_localidad")[ ["casos_consumo", "casos_violencia"] ].sum().reset_index()
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


def main():
    ensure_dirs()
    if not os.path.exists(MASTER_PATH):
        raise FileNotFoundError(f"No existe {MASTER_PATH}. Corre primero join_master.py")

    df = pd.read_csv(MASTER_PATH, dtype={"anio": "Int64"})

    plot_series_bogota(df)
    plot_top_bars(df)
    plot_heatmaps(df)
    plot_scatter(df)

    print("Figuras generadas en docs/figs/")


if __name__ == "__main__":
    main()
