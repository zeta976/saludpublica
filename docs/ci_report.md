# Intervalos de confianza para indicadores clave (IC 97%)

Este reporte utiliza métodos apropiados para conteos de eventos poco frecuentes y proporciones:

- Tasas por 100.000: IC de Byar (aprox. Poisson) para agregados de Bogotá por año.
- Proporciones: IC de Wilson para la fracción de celdas localidad–año con VIF > Consumo, comparando 2015–2019 vs 2020–2024.
- Razón de tasas (RR): IC log-normal para comparar violencia entre celdas con consumo alto (Q4) vs bajo (Q1).

## 1) Bogotá: tasas con IC (Byar)

Se muestran dos figuras: consumo y violencia, cada una con su banda de IC.

Archivos: docs/figs/bogota_tasas_ic_consumo.png y docs/figs/bogota_tasas_ic_violencia.png

## 2) Proporción (Wilson) — VIF > Consumo

| periodo   |   k |   n |        p |       lo |       hi |
|:----------|----:|----:|---------:|---------:|---------:|
| 2015–2019 |  91 |  95 | 0.957895 | 0.884416 | 0.985431 |
| 2020–2024 |  85 |  95 | 0.894737 | 0.803401 | 0.946467 |

Archivo: docs/figs/prop_vif_mayor_consumo_wilson.png

Interpretación: el porcentaje estimado indica la fracción de combinaciones localidad–año donde la tasa de violencia supera a la de consumo. El intervalo de confianza 97% refleja la incertidumbre debida al tamaño de muestra.

## 3) Razón de tasas de violencia (alto vs bajo consumo)

|   k_low |       e_low |   k_high |      e_high |     rr |      lo |      hi |
|--------:|------------:|---------:|------------:|-------:|--------:|--------:|
|  111833 | 1.35442e+07 |    41093 | 4.03404e+06 | 1.2337 | 1.21786 | 1.24975 |

Archivo: docs/figs/rr_violencia_alto_vs_bajo_consumo.png

Interpretación: RR>1 sugiere mayor riesgo de violencia en las celdas con tasas de consumo en el cuartil superior respecto al cuartil inferior, tras ajustar por población mediante tasas. El IC indica el rango compatible con los datos; si incluye 1, la evidencia no es concluyente para una diferencia.
