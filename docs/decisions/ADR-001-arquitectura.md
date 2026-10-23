# ADR-001: Monolito cliente-servidor por capas con API REST

## Estado
Aprobado (23/10/2026)

## Fecha
23/10/2026

## Contexto

La tesis pide una arquitectura web cliente-servidor responsiva con almacenamiento en la nube (D1 Tabla 2, D3). El glosario de D1 define API, backend, frontend y base de datos relacional.

Restricciones del proyecto:
- Un solo desarrollador, con nivel básico a intermedio (P-1).
- Presupuesto de infraestructura de $0 (P-6).
- Una sola instalación compartida por varios talleres (P-2).
- Prioridad a la simplicidad y a que el diseño sea fácil de defender en la sustentación.

## Decisión

Construir **un monolito** con estas características:

- **Modelo de despliegue:** cliente-servidor.
- **Organización interna del backend:** cuatro capas, en este orden:
  1. **API:** rutas, autenticación y validación de la entrada.
  2. **Servicios:** reglas de negocio y filtro por taller.
  3. **Acceso a datos:** ORM con consultas parametrizadas.
  4. **Base de datos:** PostgreSQL.
- **Dirección de dependencias:** cada capa solo usa la siguiente. Las reglas de negocio viven **únicamente** en la capa de servicios.
- **Comunicación:** API REST que intercambia JSON, versionada con el prefijo `/api/v1`.
- **Interfaz:** una aplicación React de una sola página (SPA) que consume la API.
- **Despliegue único:** en producción el mismo backend sirve la SPA ya compilada, desde el mismo dominio. No hace falta configurar CORS y hay un solo servicio que operar.

**Despliegue gratuito (P-6):**

| Componente | Opción | Candidato |
|---|---|---|
| Aplicación (API + SPA) | Servicio web de plan gratuito en una plataforma de despliegue (PaaS) | Render |
| Base de datos | PostgreSQL administrado de plan gratuito | Neon |

Las condiciones de esos planes (suspensión por inactividad, límites, vencimientos) **se verifican en la Fase 8**, porque cambian con frecuencia.

**Portabilidad:**
- Toda la configuración se lee de variables de entorno: `DATABASE_URL`, `SECRET_KEY`, `ENTORNO` y `ORIGEN_PUBLICO`.
- No se usan funciones propias de ningún proveedor.
- Pasar a otro proveedor, gratuito o de pago, consiste en cambiar el valor de esas variables.

## Alternativas consideradas

### MVC con vistas generadas en el servidor (Flask o FastAPI + Jinja)
- **Ventajas:**
  - Es la opción más simple.
  - Usa una sola tecnología.
- **Desventajas:**
  - La experiencia en el celular es menos ágil.
  - No deja una API reutilizable.
  - La lógica tiende a mezclarse con las plantillas.
- **Decisión:** rechazada como primera opción. Queda como **plan B** si falla el punto de control de React (ver ADR-004).

### Frontend y backend desplegados por separado
- **Desventajas:**
  - Exige configurar CORS.
  - Exige cookies entre dominios distintos.
  - Son dos servicios gratuitos que mantener.
- **Decisión:** rechazada por la carga operativa que implica para una sola persona.

### Microservicios
- **Decisión:** rechazada. El proyecto la excluye explícitamente y sería sobreingeniería para este alcance.

## Consecuencias

**Positivas:**
- Un solo repositorio y un solo despliegue.
- Las reglas de negocio se pueden probar de forma aislada.
- La API queda documentada en OpenAPI, lo que sirve para la sustentación.

**Negativas:**
- Hay dos herramientas de compilación: Python para el backend y Node.js para el frontend.
- El plan gratuito puede tardar en responder después de un periodo de inactividad (riesgo R-07).

## Trazabilidad

- D1: §2.2.1 (Arquitectura Web), Tabla 2 y glosario.
- D3: sección Arquitectura.
- Decisiones del autor: P-1, P-2 y P-6.
- SPEC: §8.
