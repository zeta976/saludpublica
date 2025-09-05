# Documentación de datos (proyecto bioestadística)

## 1. Recepción y almacenamiento inicial

- Archivos originales recibidos y preservados en `data/raw/`:
  - `data/raw/vintrafamiliar.csv` (fuente: SIVIM, violencia intrafamiliar y de género). Periodicidad: semestral. Serie disponible: 2013–2025 pp (junio). Fecha de recepción: [completar]. Remitente: [completar]. Formato: CSV delimitado por `;`.
  - `data/raw/psicoactivas.xlsx` (fuente: VESPA, consumo abusivo de SPA). Periodicidad: trimestral. Serie disponible: 2015–2024; preliminar 2025-T1. Fecha de recepción: [completar]. Remitente: [completar]. Formato: XLSX.

- Copias de trabajo a crear en `data/working/` (una vez normalizado encoding y delimitadores) para no modificar los archivos originales.

## 2. Revisión de formatos y encoding

- `vintrafamiliar.csv`:
  - Delimitador: `;` (punto y coma).
  - Encoding observado: presencia de mojibake en acentos (ej.: `Usaqu‚n`, `Ciudad Bol¡var`, `V¡a P£blica`), lo que sugiere Windows-1252/Latin-1 mal interpretado. Se recomienda leerlo como `encoding="latin1"` o `cp1252` y regrabar a UTF-8.
  - Tipos esperados:
    - Numéricas enteras: `ano` (año), `estrato`, indicadores binarios (`gestante`, `agresor_consumospa`, `victima_consumospa`).
    - Categóricas texto: `grupoedad`, `sexo`, `NOMBRE_LOCALIDAD`, `tipoaseguramiento`, `entidadadministradora`, `relacion_agresor`, `orientacion_sexual`, `pais_procedencia`, `ciclo_vital`, `estado_civil`, `nivel_educativo`, y los campos `lugocurrencia*`.

- `psicoactivas.xlsx`:
  - Tamaño ~7MB; inspección directa pendiente por limitaciones de visualización. Acción pendiente: listar hojas y columnas, y verificar si hay columnas de período (año/mes/trimestre), sustancia, localidad, aseguradora, sexo, curso de vida, etc. Confirmar si hay campo de conteo/casos por registro.

## 3. Normalización de nombres de variables (convención)

- Convención: minúsculas con guion bajo (snake_case); sin tildes; máximo descriptivo; prefijos consistentes.
- Mapeo propuesto (violencia intrafamiliar):
  - `ano` → `anio`
  - `NOMBRE_LOCALIDAD` → `nombre_localidad`
  - `grupoedad` → `grupo_edad`
  - `tipoaseguramiento` → `tipo_aseguramiento`
  - `entidadadministradora` → `entidad_administradora`
  - `relacion_agresor` → `relacion_agresor`
  - `orientacion_sexual` → `orientacion_sexual`
  - `gestante` → `gestante`
  - `estrato` → `estrato`
  - `pais_procedencia` → `pais_procedencia`
  - `ciclo_vital` → `ciclo_vital`
  - `estado_civil` → `estado_civil`
  - `nivel_educativo` → `nivel_educativo`
  - `agresor_consumospa` → `agresor_consumo_spa`
  - `victima_consumospa` → `victima_consumo_spa`
  - `lugocurrenciaemocional` → `lugar_ocurrencia_emocional`
  - `lugocurrenciafisica` → `lugar_ocurrencia_fisica`
  - `lugocurrenciasexual` → `lugar_ocurrencia_sexual`
  - `lugocurrenciaeconomica` → `lugar_ocurrencia_economica`
  - `lugocurrencianegligencia` → `lugar_ocurrencia_negligencia`
  - `lugocurrenciaabandono` → `lugar_ocurrencia_abandono`

- Para `psicoactivas.xlsx`: se aplicará la misma convención al identificar sus columnas (p. ej., `anio`, `nombre_localidad`, `sustancia`, `sexo`, `curso_vida`, `casos`).

## 4. Tokens de no respuesta y recodificación propuesta

- Tokens detectados en `vintrafamiliar.csv`: `"Sin dato"` (posible variación de mayúsculas/espacios). Acciones:
  - Unificar a `NA` en variables numéricas u ordinales.
  - Unificar a la categoría explícita `no_reporta` en variables categóricas.
- Cuidado: en variables binarias (`gestante`, `agresor_consumo_spa`, `victima_consumo_spa`) el valor `0` significa ausencia (no es missing). No recodificar `0` a NA.

## 5. Estandarización de localidades y códigos oficiales

- Acción pendiente: construir tabla de correspondencia `nombre_localidad` ↔ `codigo_localidad_dane` usando catálogo oficial DANE/SDP para Bogotá. Pasos:
  1) Normalizar texto (trim, mayúsculas, eliminar tildes) para emparejamiento robusto.
  2) Resolver variantes/errores ortográficos (ej.: `Los Mártires` vs `Mártires`).
  3) Validar manualmente coincidencias ambiguas y dejar registro.

## 6. Alineación temporal

- Unidad primaria de análisis: año. Acciones:
  - Violencia: agregar conteos a nivel `nombre_localidad`–`anio` (conteo de registros o uso de campo contador si existiera).
  - Consumo SPA: agregar a `nombre_localidad`–`anio` (sumar casos sobre mes/trimestre si aplica).
  - Rango de estudio: 2015–2024 (preliminar 2025-T1 se mantendrá documentado pero fuera del dataset principal, salvo decisión distinta).

## 7. Próximos pasos operativos

- Leer `vintrafamiliar.csv` como Latin-1/CP1252 y regrabar a UTF-8 en `data/working/` con delimitador `,`.
- Inspeccionar `psicoactivas.xlsx` (hojas, columnas) y aplicar convención de nombres.
- Preparar diccionario de datos y log de cambios (ver `docs/`).