# Diccionario de datos

Este documento describe las variables, tipos, dominios esperados y notas para las bases del proyecto.

## 1) Violencia intrafamiliar y de género (SIVIM)

- Origen: `data/raw/vintrafamiliar.csv`
- Periodicidad: semestral
- Unidad de registro: víctima/evento
- Cobertura temporal: 2013–2025 pp (junio)

Variables observadas (nombres originales → nombre estandarizado snake_case):

- `ano` → `anio`
  - Tipo: entero
  - Rango esperado: 2013–2025
  - Notas: se filtrará a 2015–2024 para análisis principal.

- `grupoedad` → `grupo_edad`
  - Tipo: categórica (texto)
  - Ejemplos: "De 1 - 5 años", "De 14 - 17 años" (normalizar tildes)
  - Notas: se armonizará con `ciclo_vital` si aplica.

- `sexo` → `sexo`
  - Tipo: categórica (texto)
  - Dominios: {"Hombres", "Mujeres"}

- `NOMBRE_LOCALIDAD` → `nombre_localidad`
  - Tipo: categórica (texto)
  - Dominios: 20 localidades de Bogotá D.C. (incluye Sumapaz)
  - Notas: se emparejará a `codigo_localidad_dane` con catálogo oficial.

- `tipoaseguramiento` → `tipo_aseguramiento`
  - Tipo: categórica (texto)
  - Ejemplos: {"Contributivo", "Subsidiado", "Vinculado", "Particular"}

- `entidadadministradora` → `entidad_administradora`
  - Tipo: categórica (texto)
  - Ejemplos: nombres de EPS/EPSS

- `relacion_agresor` → `relacion_agresor`
  - Tipo: categórica (texto)
  - Ejemplos: {"Madre", "Padre", "Pareja", "Padrastro", "Desconocido"}

- `orientacion_sexual` → `orientacion_sexual`
  - Tipo: categórica (texto)
  - Valores faltantes frecuentes: "Sin dato"

- `gestante` → `gestante`
  - Tipo: binaria (0/1)
  - Notas: coherencia con `sexo` se validará (hombres con `gestante = 1` → inconsistencia)

- `estrato` → `estrato`
  - Tipo: categórica ordinal {1,2,3,4,5,6} + `no_reporta`
  - Notas: valores "Sin dato" → `no_reporta`

- `pais_procedencia` → `pais_procedencia`
  - Tipo: categórica (texto)
  - Ejemplos: {"COLOMBIA", ...}

- `ciclo_vital` → `ciclo_vital`
  - Tipo: categórica (texto)
  - Ejemplos: {"Primera Infancia", "Adolescencia", ...}

- `estado_civil` → `estado_civil`
  - Tipo: categórica (texto)
  - Ejemplos: {"Soltero(a)", "Union libre"}

- `nivel_educativo` → `nivel_educativo`
  - Tipo: categórica ordinal
  - Ejemplos: {"No fue a la escuela", "Primaria incompleta", "Secundaria completa", "Universidad completa"}
  - Notas: se definirá codificación ordinal para análisis.

- `agresor_consumospa` → `agresor_consumo_spa`
  - Tipo: binaria (0/1)

- `victima_consumospa` → `victima_consumo_spa`
  - Tipo: binaria (0/1)

- `lugocurrenciaemocional` → `lugar_ocurrencia_emocional`
- `lugocurrenciafisica` → `lugar_ocurrencia_fisica`
- `lugocurrenciasexual` → `lugar_ocurrencia_sexual`
- `lugocurrenciaeconomica` → `lugar_ocurrencia_economica`
- `lugocurrencianegligencia` → `lugar_ocurrencia_negligencia`
- `lugocurrenciaabandono` → `lugar_ocurrencia_abandono`
  - Tipo: categóricas (texto)
  - Ejemplos: {"Vivienda", "Establecimiento educativo", "Vía Pública", "Lugar de trabajo", "Otro"}

Valores especiales y recodificación:

- `"Sin dato"`, `"Sin Dato"`, variaciones de espacios → recodificar a `NA` (numéricas) o `no_reporta` (categóricas)
- `0` en binarias significa ausencia, no missing.

## 2) Consumo abusivo de SPA (VESPA)

- Origen: `data/raw/psicoactivas.xlsx`
- Periodicidad: trimestral
- Unidad de registro: caso/registro VESPA
- Cobertura temporal: 2015–2024; preliminar 2025-T1

Variables esperadas (pendiente confirmar con inspección):

- `anio` (entero)
- `trimestre` o `mes` (entero)
- `nombre_localidad` (texto)
- `sexo` (texto)
- `curso_vida` (texto)
- `sustancia` (texto; principales SPA)
- `aseguradora` (texto)
- `grupo_poblacional` (texto)
- `casos` (entero; contador)

Notas de integración:

- Para análisis anual, agregar por `nombre_localidad`–`anio` sumando `casos`.
- Alinear `nombre_localidad` con catálogo DANE y con la base SIVIM.
- Documentar denominadores poblacionales por localidad–año para cálculo de tasas.
