# Patrones creacionales — MetroHub

Documentación del curso integrada en el backend FastAPI.

## 1. Builder (RF03)

**Ubicación:** `app/builders/programacion_builder.py`

Construye horarios y asignaciones con validación (solapamiento, 8 h) antes de persistir.

**Endpoints:**

- `POST /api/horarios/` — usa Builder internamente
- `POST /api/horarios/asignaciones` — usa Builder con validación
- `POST /api/horarios/programacion-completa` — horario + asignación opcional

## 2. Prototype (RF03 — grilla)

**Ubicación:** `app/prototypes/`

- `HorarioPrototype` — copia un horario desplazando fechas
- `AsignacionPrototype` — copia asignaciones al nuevo horario (estado `propuesta`, sin conflictos)

**Servicio:** `app/services/duplicar_semana_service.py`

**Endpoint:** `POST /api/horarios/duplicar-semana`

Duplica la programación de 7 días (semana origen → semana destino). Opcionalmente incluye asignaciones de choferes; omite slots ya existentes en destino.

Ejemplo de body:

```json
{
  "fecha_inicio_origen": "2026-05-19",
  "fecha_inicio_destino": "2026-05-26",
  "ruta_id": 1,
  "incluir_asignaciones": true
}
```

## 3. Factory Method (RF06)

**Ubicación:** `app/export/factory.py` (`ExportadorReporteFactory`)

- `POST /api/reportes/exportar` — formato `pdf` | `xlsx`

## 4. Abstract Factory (RF06)

**Ubicación:** `app/factories/reporte_atu_factory.py`

Ensambla secciones coherentes (encabezado, KPIs, tabla) + exportador del mismo formato.
Activado con `usar_familia_atu: true` en exportar reporte.

## Próximos pasos

- Sustituir exportadores stub por librerías PDF/XLSX en producción.
