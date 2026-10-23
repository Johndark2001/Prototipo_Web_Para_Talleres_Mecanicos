# ADR-002: FastAPI como framework de backend

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

El backend debe cumplir tres funciones:

- Exponer una API REST (ADR-001).
- Validar toda la entrada en el punto donde llega al sistema.
- Aplicar reglas de negocio que dependen de transacciones: estados de la orden, stock y liquidación.

Lo desarrolla una sola persona con conocimientos de Python (P-1). La documentación de la API sirve además como evidencia en la sustentación.

## Decisión

Usar **Python 3.13 con FastAPI** y estas herramientas:

| Herramienta | Uso |
|---|---|
| Pydantic | Esquemas de entrada y salida; validación de datos |
| SQLAlchemy 2 | Acceso a la base de datos con consultas parametrizadas |
| Alembic | Migraciones del esquema de la base de datos |
| pytest | Pruebas |
| argon2id | Hash de contraseñas (la biblioteca concreta se fija en la Fase 1) |
| Uvicorn | Servidor ASGI que ejecuta la aplicación |

## Alternativas consideradas

### Flask

- **A favor:** es muy simple y tiene una comunidad enorme.
- **En contra:** la validación y la documentación OpenAPI necesitan extensiones adicionales.
- **Decisión:** se rechaza porque implica más trabajo manual para una sola persona.

### Node.js con Express

- **A favor:** se usaría un único lenguaje en backend y frontend.
- **En contra:**
  - Hay que ensamblar varias librerías por separado.
  - Sin TypeScript no hay verificación de tipos.
  - El autor domina mejor Python.
- **Decisión:** se rechaza.

## Consecuencias

**Positivas:**
- La documentación interactiva de la API (Swagger) se genera sola.
- Los errores de validación siempre usan el mismo formato (código 422).
- Cada capa recibe y entrega datos con tipos explícitos.

**Negativas:**
- Hay que aprender la inyección de dependencias y Pydantic. La curva es moderada.

**Reglas que se derivan de esta decisión:**
- Las rutas de la API no contienen lógica de negocio: validan los datos y delegan en la capa de servicios.
- Las pruebas se ejecutan contra PostgreSQL, no contra SQLite, para que se apliquen las mismas restricciones que en producción.

## Trazabilidad

- D1: §2.2.1 Ingeniería de Software; glosario (API, Backend).
- SPEC: §8, §10 y §15.
