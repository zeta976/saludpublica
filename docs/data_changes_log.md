# Log de cambios de datos

Este documento registra transformaciones, correcciones y decisiones tomadas durante la preparación de datos.

Formato sugerido:
- Fecha
- Responsable
- Origen/Archivo
- Descripción del cambio
- Justificación/Notas

---

## 2025-09-05
- Responsable: [tu_nombre]
- Origen: `data/raw/vintrafamiliar.csv`
- Cambio: Se diagnosticó delimitador `;` y encoding Windows-1252/Latin-1. Se planificó lectura con `encoding=latin1` y regrabación a UTF-8 en `data/working/`.
- Justificación: Evitar mojibake en nombres de localidades y valores categóricos con tildes.

## 2025-09-05
- Responsable: [tu_nombre]
- Origen: `data/raw/psicoactivas.xlsx`
- Cambio: Se dejó pendiente la inspección de hojas y columnas por tamaño; se documentará en cuanto se liste la estructura.
- Justificación: Limite de visualización actual; se resolverá con script local usando `openpyxl`.
