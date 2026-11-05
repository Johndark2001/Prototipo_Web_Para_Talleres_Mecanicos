# Historial de commits del proyecto

Registro de los hitos del desarrollo de Taller Digital. Sirve para identificar las versiones importantes durante la sustentación, el mantenimiento y la evolución del sistema. El detalle de cada decisión está en el [SPEC](../SPEC.md) §21.

| Hash corto | Tipo | Descripción |
|------------|------|-------------|
| a314c7c | Semana 1 | Cierra la Fase 0 e implementa la Semana 1 del MVP |
| e02fcb3 | Semana 2 | Implementa la Semana 2 del MVP: clientes y vehículos |
| fb3f819 | Semana 3 | Implementa la Semana 3 del MVP: órdenes, estados y asignación |
| ee5c2f4 | Semana 4 | Implementa la Semana 4 del MVP: inventario, liquidación y seguimiento |
| 84f20f3 | Anonimización | Implementa la anonimización del cliente (RN-11 y RNF-06) |
| e4a164a | Documentación | Agrega la documentación de sustentación y cierra la versión previa a la Semana 5 |
| e4692f8 | Documentación | Agrega el historial de commits del proyecto |
| 2faf3c0 | Herramientas | Agrega las skills de diseño y su guía de uso para el rediseño visual |
| e3fc487 | Rediseño | Rediseña la interfaz y agrega el tipo de vehículo (carro o moto) |
| e51d187 | Cambios #4–#6 | Reorganiza la orden, agrega el informe PDF, la categoría del problema y el alta de cliente con vehículo |
| 464e261 | Documentación | Registra la aprobación de las decisiones O-1 a O-9 |

## Detalle de cada hito

| Hash completo | Fecha | Migración | Pruebas | Decisiones (SPEC) |
|---|---|---|---|---|
| `a314c7c5b38d60a9998576ac946c6b41073156f8` | 23/10/2026 | 0001 | 25 | P-1 a P-9, H-1 a H-5 (§21.1–21.3) |
| `e02fcb3b5d2ad8b17bbdf5cccfbcf8441ff8e410` | 25/10/2026 | 0002 | — | S2-1 a S2-5 (§21.4) |
| `fb3f81933ac38cdf5dfbab57a8df099ddb8c1f8c` | 25/10/2026 | 0003 | — | S3-1 a S3-7 (§21.5) |
| `ee5c2f427b591243bef3d091a932f93dad3d7e02` | 26/10/2026 | 0004 | 194 | S4-1 a S4-9 (§21.6) |
| `84f20f34cfc8a8fc49956a507d66e4f5a5206b29` | 28/10/2026 | 0005 | 214 | A-1 a A-7 (§21.7) |
| `e4a164ae0b84d164205242901290210f578e3506` | 28/10/2026 | 0005 (sin cambios) | 214 | Cierre previo a la Semana 5 (§21.8) |
| `e4692f8fa01610d4a78f1418c2fe8d54c45886e3` | 28/10/2026 | 0005 (sin cambios) | 214 | — (solo documentación) |
| `2faf3c004d45941aa4aa858f7fa554eb006b0f59` | 03/11/2026 | 0005 (sin cambios) | 214 | — (skills en `.claude/skills/` y [guía](guia-skills-diseno.md)) |
| `e3fc487476eb1aa70ea907c79771eef9afe38af4` | 04/11/2026 | 0006 | 224 | V-1 a V-5 (§21.9) |
| `e51d1874a43da5d25cab760562cbe25e0a949665` | 04/11/2026 | 0007 | 263 | O-1 a O-9 (§21.10) |
| `464e2614e27d9067c8b70b3991442d53b0a9777b` | 04/11/2026 | 0007 (sin cambios) | 263 | Aprobación de O-1 a O-9 (§21.10) |
| Sin commit | 05/11/2026 | 0007 (sin cambios) | 263 | T-1 a T-3 (§21.11) y actualización documental (§21.12) |

«—» en Pruebas: el mensaje de ese commit no registra el total de pruebas.

## Detalle del commit `e51d187` (04/11/2026)

Cambios #4, #4B, #5 y #6 pedidos por el autor antes de la Semana 5 (decisiones O-1 a O-9, SPEC §21.10). No cambian los roles, los estados ni las transiciones.

| Cambio | Qué se hizo | Decisiones |
|---|---|---|
| #4 — Vista vertical de la orden | El detalle pasa a una sola columna: encabezado, estado, acciones, información general, diagnóstico, trabajo realizado, costos, enlace de seguimiento e historial. Diagnóstico y trabajo realizado quedan en secciones separadas | O-1 |
| #4B — Informe PDF final | `GET /ordenes/{id}/informe.pdf` y `GET /seguimiento/{codigo}/informe.pdf`, solo para órdenes `ENTREGADO` (409 en otro estado). La versión pública omite nombre, teléfono y kilometraje y enmascara la placa | O-2, O-3 |
| Dependencia nueva | **fpdf2** (Python puro), registrada también en [ADR-002](decisions/ADR-002-backend.md) | O-4 |
| #5 — Categoría del problema | Catálogo fijo por tipo de vehículo (22 para carro, 20 para moto) en `GET /catalogos/categorias-problema`; buscador sin tildes ni mayúsculas; «Otro» con descripción obligatoria; solo ADMIN y RECEPCION la registran | O-5, O-7 |
| #5 — Observación del cliente | Campo `observacion_cliente`; `motivo_ingreso` se conserva compuesto como «categoría — observación» y el API acepta todavía la forma anterior | O-5, O-6 |
| #6 — Cliente + vehículo | `POST /clientes` con un objeto `vehiculo` opcional, en una sola transacción; «Nuevo cliente» incluye «Información del vehículo» y la lista de Vehículos deja de tener botón de alta propio | O-8, O-9 |
| Migración 0007 | `orden_trabajo.categoria_problema`, `categoria_otro`, `observacion_cliente` y el CHECK `ck_orden_trabajo_categoria_otro_solo_con_otro`; copia el motivo de las órdenes anteriores a la observación y las deja sin categoría | O-6 |
| Pruebas nuevas | 39 casos más (224 → 263): `test_informe_pdf.py` (16), `test_categoria_problema.py` (17), `test_cliente_con_vehiculo.py` (6) | — |

Validación: el autor probó en local el PDF interno y público, el alta de cliente con vehículo, las categorías, la observación y la vista de la orden. Aprobación registrada en `464e261`.

# Última versión estable

Hash:

e51d187 (`e51d1874a43da5d25cab760562cbe25e0a949665`)

Descripción:

MVP con la vista vertical de la orden, el informe PDF final, la categoría del problema y el alta de cliente con vehículo (SPEC §21.10, aprobadas el 04/11/2026). Validado por el autor en entorno local con datos ficticios; todavía no está desplegado.

**Cambios posteriores sin commit (05/11/2026):** terminología «Cliente» en lugar de «Dueño» y fondos temáticos por módulo (SPEC §21.11), y la actualización de la documentación (§21.12).

# Funcionalidades implementadas

- Usuarios y roles.
- Clientes.
- Vehículos, de tipo carro o moto, con filtro por tipo combinado con la placa.
- Órdenes de trabajo.
- Estados e historial.
- Asignación de mecánicos.
- Inventario.
- Repuestos.
- Liquidación.
- Seguimiento público.
- Dashboard (versión mínima: órdenes por estado, entregados hoy y alertas de stock).
- Anonimización.
- Categoría del problema y observación del cliente (catálogo por tipo de vehículo).
- Informe PDF final de la orden entregada (interno y desde el seguimiento público).
- Alta de cliente con su primer vehículo en una sola operación.
- Rediseño visual, terminología «Cliente» y fondos temáticos por módulo.
- Documentación de sustentación ([docs/sustentacion/](sustentacion/README.md)).

# Pendientes para la Semana 5

- Despliegue en Render.
- Base de datos Neon.
- HTTPS.
- Dashboard completo.
- Reportes RF-15.
- Seguridad adicional.
- Cobertura RNF-09.

## Cómo mantener este documento

Al cerrar cada hito aprobado, agregue una fila en las dos tablas y actualice «Última versión estable». Para ver el historial completo:

```
git log --reverse --format="%h  %ad  %s" --date=short
```
