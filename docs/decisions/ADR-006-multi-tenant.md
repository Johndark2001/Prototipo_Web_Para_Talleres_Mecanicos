# ADR-006: Multi-tenant con aislamiento lógico por `taller_id`

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

El piloto se hace en varios talleres (D1 §3.2.3) con **una sola instalación** compartida (P-2). Lo mantiene un único desarrollador y no hay presupuesto (P-1, P-6).

Cada taller solo debe ver sus propios clientes, vehículos, órdenes, inventario y usuarios. Si los datos de un taller quedaran visibles para otro, se violaría la Ley 1581 y se perdería la confianza de los talleres.

## Decisión

### Modelo

Todos los talleres comparten **una base de datos y un esquema**. El aislamiento es lógico:

- **Tablas raíz** (llevan la columna `taller_id NOT NULL` con FK a `taller`): `usuario`, `cliente`, `vehiculo`, `orden_trabajo`, `servicio` y `repuesto`.
- **Tablas hijas** (heredan el taller de su tabla padre y **no** repiten `taller_id`):
  - `historial_estado_orden`, `asignacion_orden`, `orden_servicio` y `orden_repuesto` dependen de la orden;
  - `movimiento_inventario` depende del repuesto.

Las restricciones de unicidad se definen **por taller**:

- `(taller_id, placa)`
- `(taller_id, numero)`
- `(taller_id, codigo)` en repuestos
- `(taller_id, nombre)` en servicios

Hay dos excepciones que son únicas en todo el sistema:

- `usuario.email`: el inicio de sesión no pide elegir el taller.
- `codigo_seguimiento`: el enlace público no lleva el taller.

### Cómo se garantiza el aislamiento

1. **El taller sale siempre de la sesión.** El `taller_id` se toma del usuario autenticado (ADR-005). Nunca se acepta desde el cuerpo de la solicitud, la URL ni los parámetros.
2. **Una sola puerta de entrada a los datos.** La capa de servicios es el único lugar que consulta las tablas raíz, y siempre agrega el filtro `taller_id = :taller_del_usuario`. Las tablas hijas se acceden únicamente a través de una tabla padre que ya fue verificada.
3. **Referencias cruzadas verificadas.** Al crear o modificar un registro que apunta a otro (por ejemplo, una orden que apunta a un vehículo, a un mecánico o a un repuesto), el servicio confirma que el registro referenciado pertenece al mismo taller. Si no es así, responde "no encontrado".
4. **Respuesta ante otro taller.** Pedir un recurso de otro taller produce `404`, nunca `403`, para no revelar que el recurso existe.
5. **Pruebas obligatorias.** Cada recurso tiene al menos una prueba automatizada que intenta leer y modificar datos de otro taller y espera un `404`.

### Alta de talleres

No existe un rol de superadministrador ni una pantalla para crear talleres. Esto queda fuera del alcance (SPEC §2.2).

El desarrollador crea cada taller y su primer usuario `ADMIN` con un **script de administración** que se ejecuta en el servidor. A partir de ahí, el `ADMIN` crea los demás usuarios de su taller desde la aplicación (RF-16).

## Alternativas consideradas

| Alternativa | Por qué se rechaza |
|---|---|
| Una base de datos por taller | Con 10 talleres serían 10 bases que mantener y migrar. Inviable en un plan gratuito y para una sola persona. |
| Un esquema de PostgreSQL por taller | Cada migración habría que aplicarla N veces. Complejidad que no se justifica en un MVP. |
| Row-Level Security (RLS) de PostgreSQL | Es más robusta, pero exige configurar una variable de sesión en cada conexión y es difícil de depurar para un desarrollador que empieza. Queda como **mejora futura**: el modelo ya la soporta porque las tablas raíz tienen `taller_id`. |
| Llaves foráneas compuestas `(taller_id, id)` en todas las referencias | Garantizan el aislamiento desde la base de datos, pero duplican `taller_id` en todas las tablas hijas y complican el modelo. Se sustituyen por la verificación en la capa de servicios (punto 3) junto con las pruebas (punto 5). |

## Consecuencias

**Positivas:**
- Un solo despliegue, una sola migración y un solo respaldo.
- Los reportes se pueden comparar entre talleres para la tesis, usando datos anónimos.

**Negativas:**
- El aislamiento depende de la disciplina en la capa de servicios. Un olvido expondría datos. Por eso las pruebas de aislamiento son **obligatorias** (RNF-05).

**Riesgo residual:** el riesgo R-05 del SPEC. Se revisa de nuevo en la Fase 7.

## Trazabilidad

- D1: §3.2.3 (muestra de 10 talleres) y §3.6 (Ley 1581).
- Decisión del autor: P-2.
- SPEC: §3, RN-09 y RNF-05.
- Modelo de datos: docs/modelo-datos.md.
