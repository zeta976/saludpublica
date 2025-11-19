import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

RATES_PATH = os.path.join("data", "working", "localidad_ano_master_rates.csv")
FIG_DIR = os.path.join("docs", "figs")
REPORT = os.path.join("docs", "regression_report.md")

sns.set(style="whitegrid", context="talk")


def ensure_dirs():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)


def load_data() -> pd.DataFrame:
    if not os.path.exists(RATES_PATH):
        raise FileNotFoundError(f"No existe {RATES_PATH}. Corre primero compute_rates.py")
    df = pd.read_csv(RATES_PATH, dtype={"anio": "Int64"})
    # Mantener filas con información básica completa
    df = df.dropna(subset=["tasa_consumo_100k", "tasa_violencia_100k", "poblacion", "anio", "nombre_localidad"]).copy()
    df["anio"] = df["anio"].astype(int)
    return df


def fit_panel_ols(df: pd.DataFrame):
    """Modelo de regresión múltiple a nivel localidad–año.

    Dependiente: tasa_violencia_100k
    Predictores: tasa_consumo_100k (exposición principal), año centrado, efecto fijo por localidad.
    """
    df = df.copy()
    df["anio_c"] = df["anio"] - df["anio"].mean()

    X_base = df[["tasa_consumo_100k", "anio_c"]]
    dummies = pd.get_dummies(df["nombre_localidad"], drop_first=True)
    X = pd.concat([X_base, dummies], axis=1)
    X = sm.add_constant(X)
    y = df["tasa_violencia_100k"]

    model = sm.OLS(y, X).fit(cov_type="HC3")  # errores robustos heterocedasticidad
    return model


def aggregate_city(df: pd.DataFrame) -> pd.DataFrame:
    """Serie de tiempo de Bogotá (tasas agregadas por año)."""
    city = (
        df.groupby("anio", dropna=True)
        .agg(
            casos_consumo=("casos_consumo", "sum"),
            casos_violencia=("casos_violencia", "sum"),
            poblacion=("poblacion", "sum"),
        )
        .reset_index()
    )
    city["tasa_consumo_100k"] = city["casos_consumo"] / city["poblacion"] * 100000
    city["tasa_violencia_100k"] = city["casos_violencia"] / city["poblacion"] * 100000
    return city


def fit_city_ols(city: pd.DataFrame):
    """Modelo de regresión para Bogotá por año con uso para pronóstico."""
    city = city.copy()
    city["anio_c"] = city["anio"] - city["anio"].mean()
    X = city[["tasa_consumo_100k", "anio_c"]]
    X = sm.add_constant(X)
    y = city["tasa_violencia_100k"]
    model = sm.OLS(y, X).fit()
    return model


def plot_panel_scatter(df: pd.DataFrame, model):
    """Scatter localidad–año con recta de regresión global."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        x="tasa_consumo_100k",
        y="tasa_violencia_100k",
        hue="anio",
        palette="viridis",
        alpha=0.7,
        ax=ax,
    )
    # Recta ajustada manteniendo año centrado en 0 y localidad de referencia
    cons_vals = np.linspace(df["tasa_consumo_100k"].min(), df["tasa_consumo_100k"].max(), 100)
    anio_c0 = 0.0
    # construir X con localidad de referencia (todas dummies=0)
    X_line = pd.DataFrame({"tasa_consumo_100k": cons_vals, "anio_c": anio_c0})
    X_line = sm.add_constant(X_line, has_constant="add")
    # asegurar mismas columnas que el modelo
    for col in model.model.exog_names:
        if col not in X_line.columns and col != "const":
            X_line[col] = 0.0
    X_line = X_line[model.model.exog_names]
    y_pred = model.predict(X_line)
    ax.plot(cons_vals, y_pred, color="red", linewidth=2, label="Recta ajustada (año medio)")

    ax.set_title("Relación entre tasas de consumo y violencia (localidad–año)")
    ax.set_xlabel("Tasa de consumo por 100.000 hab.")
    ax.set_ylabel("Tasa de violencia por 100.000 hab.")
    ax.legend()

    path = os.path.join(FIG_DIR, "reg_panel_scatter_tasas.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Guardado: {path}")


def plot_city_series_with_fit(city: pd.DataFrame, model):
    """Serie de tiempo de Bogotá con predicción in-sample y pronóstico para 2025–2026."""
    city = city.copy()
    city["anio_c"] = city["anio"] - city["anio"].mean()

    # Predicción in-sample
    X_in = sm.add_constant(city[["tasa_consumo_100k", "anio_c"]])
    city["pred"] = model.predict(X_in)

    # Escenario de pronóstico: mantener la tasa de consumo igual al nivel de 2024 y extrapolar años 2025–2026
    last_year = city["anio"].max()
    tasa_cons_2024 = city.loc[city["anio"] == last_year, "tasa_consumo_100k"].iloc[0]

    future_years = [last_year + 1, last_year + 2]
    future = pd.DataFrame({"anio": future_years})
    future["tasa_consumo_100k"] = tasa_cons_2024
    future["anio_c"] = future["anio"] - city["anio"].mean()
    X_future = sm.add_constant(future[["tasa_consumo_100k", "anio_c"]])
    future["pred"] = model.predict(X_future)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(city["anio"], city["tasa_violencia_100k"], marker="o", label="Observado")
    ax.plot(city["anio"], city["pred"], linestyle="--", marker="o", label="Ajustado")
    ax.plot(future["anio"], future["pred"], linestyle=":", marker="o", color="red", label="Pronóstico")

    ax.set_title("Bogotá: tasas de violencia observadas, ajustadas y pronosticadas")
    ax.set_xlabel("Año")
    ax.set_ylabel("Tasa de violencia por 100.000 hab.")
    ax.legend()

    path = os.path.join(FIG_DIR, "reg_bogota_series_forecast.png")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Guardado: {path}")

    return future


def main():
    ensure_dirs()
    df = load_data()

    # Modelo panel localidad–año
    panel_model = fit_panel_ols(df)

    # Modelo de ciudad y pronóstico
    city = aggregate_city(df)
    city_model = fit_city_ols(city)
    future = plot_city_series_with_fit(city, city_model)

    # Scatter panel
    plot_panel_scatter(df, panel_model)

    # Guardar resumen en markdown
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Modelos de regresión y pronósticos\n\n")
        f.write("## 1) Modelo de regresión múltiple localidad–año (OLS)\n\n")
        f.write("Dependiente: tasa_violencia_100k. Predictores: tasa_consumo_100k, año centrado y efectos fijos por localidad.\n\n")
        f.write(panel_model.summary().as_text())
        f.write("\n\n")

        f.write("## 2) Modelo de regresión para Bogotá por año y pronósticos\n\n")
        f.write("Dependiente: tasa_violencia_100k agregada para Bogotá. Predictores: tasa_consumo_100k y año centrado.\n\n")
        f.write(city_model.summary().as_text())
        f.write("\n\n")

        f.write("### Pronósticos de tasa de violencia (suponiendo tasa de consumo constante al nivel de 2024)\n\n")
        f.write(future.to_markdown(index=False))
        f.write("\n")

    print(f"Reporte generado: {REPORT}")


if __name__ == "__main__":
    main()
