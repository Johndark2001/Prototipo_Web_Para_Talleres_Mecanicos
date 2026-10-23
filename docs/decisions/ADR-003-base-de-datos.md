# ADR-003: PostgreSQL como base de datos

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

Los datos del sistema son relacionales:

- un cliente tiene vehículos;
- un vehículo tiene órdenes;
- una orden tiene líneas de servicios y repuestos;
- un repuesto tiene movimientos de inventario.

Algunas reglas deben cumplirse aunque el código falle:

- el stock nunca es negativo;
- la placa es única dentro de cada taller;
- un vehículo tiene como máximo una orden abierta;
- el número de orden es consecutivo dentro de cada taller.

Además:

- Varios usuarios escriben al mismo tiempo y varios talleres comparten la misma instalación (P-2).
- El glosario de D1 define "base de datos relacional".
- La base de datos debe poder alojarse gratis (P-6).

## Decisión

Usar **PostgreSQL 17**. La versión 18 también es compatible.

| Entorno | Dónde se ejecuta |
|---|---|
| Desarrollo | Instalación local |
| Pruebas | Base de datos de prueba local |
| Producción | Servicio administrado con plan gratuito (candidato: Neon, ver ADR-001) |

Las reglas críticas se garantizan también en la base de datos, no solo en el código:

| Mecanismo | Para qué se usa |
|---|---|
| Restricciones `CHECK` | Stock ≥ 0, cantidades positivas, montos no negativos |
| Índices únicos | `(taller_id, placa)`, `(taller_id, numero)` y `codigo_seguimiento` |
| Índice único parcial | Una sola orden abierta por vehículo |
| Tipos `ENUM` | Rol del usuario, estado de la orden y tipo de movimiento |
| Transacciones con bloqueo de fila (`SELECT … FOR UPDATE`) | Descontar stock y tomar el siguiente número de orden sin que dos operaciones choquen |
| Tipo `NUMERIC` | Montos y cantidades. Nunca `float`, porque introduce errores de redondeo. |

## Alternativas consideradas

### SQLite

- Solo permite un escritor a la vez.
- Las llaves foráneas vienen desactivadas por defecto.
- No hay un servicio administrado en la nube que sirva para una aplicación con varios usuarios.
- Las pruebas no se comportarían igual que producción.
- **Decisión:** se rechaza.

### MySQL

- Es una base de datos madura.
- Pero sus índices únicos parciales son menos expresivos para estas reglas.
- Y hay menos oferta gratuita administrada.
- **Decisión:** se rechaza.

## Consecuencias

**Positivas:**
- La integridad de los datos no depende solo del código.
- Las restricciones del modelo son fáciles de explicar al jurado.

**Negativas:**
- Hay que instalar PostgreSQL en el equipo de desarrollo.
- El plan gratuito limita el almacenamiento, aunque alcanza para un piloto.

**Prácticas obligatorias:**
- **Respaldo:** exportar la base de datos con `pg_dump` al menos una vez por semana durante el piloto.
- **Migraciones:** todo cambio de esquema se hace con Alembic. Nunca se modifica la base de producción a mano.

## Trazabilidad

- D1: §2.2.1 (Bases de Datos); glosario (Base de Datos Relacional, Centralización de Datos).
- SPEC: §6 y §9.
- Modelo de datos: docs/modelo-datos.md.
