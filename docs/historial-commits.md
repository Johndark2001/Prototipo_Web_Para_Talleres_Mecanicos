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

## Detalle de cada hito

| Hash completo | Fecha | Migración | Pruebas | Decisiones (SPEC) |
|---|---|---|---|---|
| `a314c7c5b38d60a9998576ac946c6b41073156f8` | 23/10/2026 | 0001 | 25 | P-1 a P-9, H-1 a H-5 (§21.1–21.3) |
| `e02fcb3b5d2ad8b17bbdf5cccfbcf8441ff8e410` | 25/10/2026 | 0002 | — | S2-1 a S2-5 (§21.4) |
| `fb3f81933ac38cdf5dfbab57a8df099ddb8c1f8c` | 25/10/2026 | 0003 | — | S3-1 a S3-7 (§21.5) |
| `ee5c2f427b591243bef3d091a932f93dad3d7e02` | 26/10/2026 | 0004 | 194 | S4-1 a S4-9 (§21.6) |
| `84f20f34cfc8a8fc49956a507d66e4f5a5206b29` | 28/10/2026 | 0005 | 214 | A-1 a A-7 (§21.7) |
| `e4a164ae0b84d164205242901290210f578e3506` | 28/10/2026 | 0005 (sin cambios) | 214 | Cierre previo a la Semana 5 (§21.8) |

«—»: el mensaje de ese commit no registra el total de pruebas.

# Última versión estable

Hash:

e4a164a (`e4a164ae0b84d164205242901290210f578e3506`)

Descripción:

MVP funcional completo y documentado antes del inicio de la Semana 5. Validado en entorno local con datos ficticios; todavía no está desplegado.

# Funcionalidades implementadas

- Usuarios y roles.
- Clientes.
- Vehículos.
- Órdenes de trabajo.
- Estados e historial.
- Asignación de mecánicos.
- Inventario.
- Repuestos.
- Liquidación.
- Seguimiento público.
- Dashboard (versión mínima: órdenes por estado, entregados hoy y alertas de stock).
- Anonimización.
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
