# Manual técnico — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Desarrolladores que mantengan el sistema y evaluadores técnicos |
| Versión del código | Commit `e51d187` (04/11/2026), migración de base de datos `0007`, más los ajustes visuales del 05/11/2026 (SPEC §21.11) |
| Documentos de referencia | [SPEC.md](../../SPEC.md), [ADR-001 a ADR-006](../decisions/), [modelo de datos](../modelo-datos.md), [README](../../README.md) |

---

## 1. Arquitectura general

### 1.1 Estilo

**Monolito cliente-servidor por capas, con API REST JSON** ([ADR-001](../decisions/ADR-001-arquitectura.md)).

- Un solo backend (FastAPI) expone la API en `/api/v1` y, cuando existe la carpeta compilada `frontend/dist`, **sirve también la interfaz** desde el mismo dominio.
- La interfaz es una aplicación React de una sola página (SPA) que consume la API con `fetch`.
- Una sola base de datos PostgreSQL atiende a **varios talleres** con aislamiento lógico por `taller_id` ([ADR-006](../decisions/ADR-006-multi-tenant.md)).

**Por qué un monolito y no microservicios:** lo desarrolla y mantiene una sola persona (P-1), sin presupuesto (P-6), y el volumen previsto es el de un piloto (decenas de usuarios y miles de órdenes). Un solo despliegue reduce los puntos de falla y el costo. El SPEC §16 prohíbe explícitamente los microservicios y Kubernetes.

```mermaid
flowchart LR
    subgraph Cliente["Navegador (celular o PC)"]
        SPA["React SPA<br/>(Vite + Tailwind)"]
        PUB["Página pública<br/>/seguimiento/:codigo"]
    end
    subgraph Servidor["Backend FastAPI (un proceso)"]
        MW["Middleware<br/>JSON obligatorio en modificaciones"]
        API["Capa API<br/>app/api"]
        SRV["Capa de servicios<br/>app/services"]
        ORM["Acceso a datos<br/>SQLAlchemy 2 (app/models)"]
        EST["Archivos estáticos<br/>frontend/dist"]
    end
    DB[("PostgreSQL 17")]

    SPA -- "HTTPS + cookie de sesión" --> MW
    PUB -- "GET sin sesión" --> MW
    MW --> API --> SRV --> ORM --> DB
    Servidor -. "sirve index.html y /assets" .-> SPA
```

### 1.2 Capas del backend

Cada capa solo depende de la siguiente (SPEC §8).

| Capa | Carpeta | Responsabilidad | Ejemplo |
|---|---|---|---|
| API | `app/api/` | Rutas HTTP, autenticación, control de rol y validación de la entrada con esquemas Pydantic | `api/ordenes.py` |
| Esquemas | `app/schemas/` | Contratos de entrada y salida; normalización (placa, teléfono, documento) y mensajes en español | `schemas/clientes.py` |
| Servicios | `app/services/` | Reglas de negocio (RN-01 a RN-21), filtro por taller, transacciones y bloqueos | `services/inventario.py` |
| Modelos | `app/models/` | Tablas, relaciones y restricciones (SQLAlchemy 2, tipado) | `models/orden.py` |
| Núcleo | `app/core/` | Configuración, conexión, seguridad, errores y límite de solicitudes | `core/seguridad.py` |

La máquina de estados de la orden está en `services/flujo_orden.py` como **reglas puras**, sin base de datos: decide qué cambio existe y quién lo puede hacer. Las condiciones que dependen de los datos (RN-13, RN-17, RN-18) se verifican en `services/ordenes.py`.

### 1.3 Tecnologías y versiones

| Capa | Tecnología | Versión declarada | ADR |
|---|---|---|---|
| Lenguaje backend | Python | 3.13 | [ADR-002](../decisions/ADR-002-backend.md) |
| Framework web | FastAPI | ≥ 0.115 | ADR-002 |
| Servidor ASGI | Uvicorn | ≥ 0.32 | ADR-002 |
| ORM | SQLAlchemy | ≥ 2.0.36 | ADR-002 |
| Migraciones | Alembic | ≥ 1.14 | ADR-002 |
| Controlador PostgreSQL | psycopg 3 | ≥ 3.2 | ADR-003 |
| Validación y configuración | Pydantic + pydantic-settings | ≥ 2.6 | ADR-002 |
| Tokens | PyJWT | ≥ 2.10 | [ADR-005](../decisions/ADR-005-autenticacion.md) |
| Hash de claves | argon2-cffi (argon2id) | ≥ 23.1 | ADR-005 |
| Informe PDF | fpdf2 (Python puro, sin binarios del sistema) | ≥ 2.8 | ADR-002 (ampliado por la decisión O-4, SPEC §21.10) |
| Base de datos | PostgreSQL | 17 | [ADR-003](../decisions/ADR-003-base-de-datos.md) |
| Interfaz | React + React Router | 19 / 8 | [ADR-004](../decisions/ADR-004-frontend.md) |
| Compilación | Vite | 8 | ADR-004 |
| Estilos | Tailwind CSS | 4 | ADR-004 |
| Gestor de Python | uv | reciente | — |
| Calidad | pytest, Ruff, ESLint | — | — |

El frontend sigue con **tres dependencias de ejecución** (`react`, `react-dom`, `react-router`). Íconos, logo, ilustraciones y fondos de los módulos son SVG propios (decisiones V-4 y T-2), sin librerías de íconos ni de imágenes.

---

## 2. FastAPI (backend)

### 2.1 Arranque de la aplicación

`app/main.py` crea la aplicación con `crear_app()`:

1. Registra los manejadores de errores (`core/errores.py`), que dan a toda respuesta de error el mismo formato.
2. Agrega el middleware `exigir_json_en_modificaciones`: toda solicitud `POST`, `PUT`, `PATCH` o `DELETE` a `/api/` que no sea `application/json` recibe **415**. Es parte de la defensa contra CSRF (un formulario HTML de otro sitio no puede enviar JSON).
3. Monta los routers bajo `/api/v1`.
4. Si existe `frontend/dist`, sirve `/assets` y devuelve `index.html` para cualquier otra ruta, que luego resuelve React Router. Las rutas `api/*` desconocidas responden 404 en JSON.

La documentación interactiva (OpenAPI) queda en `/api/docs`.

### 2.2 Endpoints

| Recurso | Método y ruta | Rol | Propósito |
|---|---|---|---|
| Salud | `GET /salud` | Público | Confirma la conexión con la base de datos |
| Autenticación | `POST /auth/login` | Público | Inicia sesión y crea la cookie |
| | `POST /auth/logout` | Público | Borra la cookie |
| | `GET /auth/me` | Sesión | Usuario y taller de la sesión |
| Usuarios | `GET /usuarios`, `POST /usuarios`, `PATCH /usuarios/{id}` | ADMIN | Listar, crear, cambiar nombre, rol o estado |
| Catálogos | `GET /catalogos/categorias-problema` | Sesión | Categorías del problema por tipo de vehículo (O-5) |
| Clientes | `GET /clientes`, `GET /clientes/{id}` | Todos | Listado con búsqueda y detalle con sus vehículos |
| | `POST /clientes` | ADMIN, RECEPCION | Crear el cliente y, si llega el objeto `vehiculo`, su primer vehículo en la misma transacción (O-8) |
| | `PATCH /clientes/{id}` | ADMIN, RECEPCION | Editar, desactivar |
| | `POST /clientes/{id}/anonimizar` | ADMIN | Anonimización (RN-11) |
| Vehículos | `GET /vehiculos`, `GET /vehiculos/{id}` | Todos | Búsqueda por placa, filtro `tipo=CARRO\|MOTO` combinable con `placa`, `activo` y `cliente_id` (V-2), y detalle |
| | `POST /vehiculos`, `PATCH /vehiculos/{id}` | ADMIN, RECEPCION | Crear (con `tipo`, por defecto `CARRO`), editar, cambiar el cliente, desactivar |
| Órdenes | `GET /ordenes`, `GET /ordenes/{id}` | Todos (el mecánico solo las suyas) | Listado filtrable y detalle |
| | `POST /ordenes` | ADMIN, RECEPCION | Abrir orden con `categoria_problema`, `categoria_otro` y `observacion_cliente` (o, en la forma anterior, solo `motivo_ingreso`) (O-5, O-6) |
| | `PATCH /ordenes/{id}` | Según campo | Datos de recepción (ADMIN, RECEPCION; el mecánico recibe 403), diagnóstico y trabajo |
| | `GET /ordenes/{id}/informe.pdf` | Quien vea la orden | Informe final; 409 si la orden no está `ENTREGADO` (O-2) |
| | `POST /ordenes/{id}/historial` | Según transición | Cambio de estado |
| | `POST /ordenes/{id}/asignaciones` | ADMIN, RECEPCION | Asignar o reasignar mecánico |
| | `POST /ordenes/{id}/servicios`, `DELETE …/servicios/{linea}` | ADMIN, RECEPCION, mecánico asignado | Mano de obra |
| | `POST /ordenes/{id}/repuestos`, `DELETE …/repuestos/{linea}` | ADMIN, RECEPCION, mecánico asignado | Repuestos con descuento y devolución de stock |
| Mecánicos | `GET /mecanicos` | ADMIN, RECEPCION | Mecánicos activos con su carga (S3-6) |
| Repuestos | `GET /repuestos` | Todos | Lista del inventario |
| | `GET /repuestos/{id}`, `POST /repuestos`, `PATCH /repuestos/{id}` | ADMIN | Detalle, alta y edición |
| | `GET /repuestos/{id}/movimientos`, `POST /repuestos/{id}/movimientos` | ADMIN | Movimientos; entradas y ajustes |
| Dashboard | `GET /dashboard` | ADMIN, RECEPCION | Conteos por estado, entregadas hoy y stock bajo |
| Seguimiento | `GET /seguimiento/{codigo}` | Público, limitado | Vista pública de la orden |
| | `GET /seguimiento/{codigo}/informe.pdf` | Público, limitado | Informe final sin datos personales; 409 si no está entregada (O-3) |

En total hay **38 operaciones** (35 en la versión `84f20f3`, más el catálogo y los dos informes). Todas las rutas llevan el prefijo `/api/v1`. El conteo sale del OpenAPI que genera la aplicación.

### 2.3 Convenciones

- **Formato de error único:** `{"error": {"code", "message", "details"}}`. Los errores de validación de Pydantic se traducen al español del taller (`core/errores.py`).
- **Códigos HTTP:** 401 sin sesión, 403 rol sin permiso, 404 inexistente u otro taller, 409 conflicto de estado o de stock, 415 cuerpo no JSON, 422 datos inválidos, 429 demasiadas solicitudes.
- **Listados** paginados con `page` y `page_size` (máximo 100); la respuesta trae `data` y `pagination`.
- **Montos y cantidades** viajan como texto decimal para no perder precisión.
- **Fechas** en ISO 8601 con zona horaria.

---

## 3. React (frontend)

### 3.1 Organización

| Carpeta | Contenido |
|---|---|
| `src/pages/` | Una pantalla por archivo: `Login`, `Dashboard`, `Ordenes`, `OrdenNueva`, `OrdenDetalle`, `Clientes`, `ClienteDetalle`, `ClienteFormulario`, `Vehiculos`, `VehiculoDetalle`, `VehiculoFormulario`, `Inventario`, `RepuestoDetalle`, `RepuestoFormulario`, `Usuarios`, `Seguimiento`, `NoEncontrada` |
| `src/components/` | Componentes reutilizables: `Boton`, `CampoFormulario`, `Aviso`, `DialogoConfirmacion`, `DialogoNota`, `ChipEstado`, `EstadoVacio`, `Esqueleto`, `EtiquetaStock`, `BuscadorPlaca`, `Layout`, `AnonimizarCliente`, `CamposVehiculo` (tipo, placa, marca, modelo, año y color; lo usan el formulario del vehículo y el alta del cliente), `FiltroTipoVehiculo` (Todos, Carros, Motos), `EtiquetaTipo`, `SelectorCliente`, `Icono`, `Logo`, `IlustracionTaller`, `FondoModulo`… |
| `src/components/orden/` | Paneles del detalle de la orden: `AccionesEstado`, `PanelMecanico`, `PanelRecepcion`, `PanelTrabajo`, `PanelLiquidacion`, `LineaTiempo`, `HistorialOrden`, `EnlaceSeguimiento`, `CamposProblema` (buscador de categorías y observación), selectores |
| `src/assets/fondos/` | Seis escenas SVG de fondo, una por módulo (T-2) |
| `src/problema.js` | Búsqueda de categorías sin tildes ni mayúsculas y composición «categoría — observación» (O-6, O-7) |
| `src/sesion/` | `ProveedorSesion` (contexto con el usuario y el taller) y `RutaProtegida` (redirige al login o bloquea por rol) |
| `src/hooks/` | `useConsulta` (GET con estados de carga y error), `useRetrasado` (espera breve antes de buscar), `useAvisoNavegacion` |
| `src/api/cliente.js` | **Único punto de acceso a la API**: `fetch` con `credentials: 'same-origin'`, JSON obligatorio y traducción de errores a `ErrorApi` |
| `src/constantes.js`, `src/formato.js` | Roles, estados, textos del taller y formato de pesos, fechas y teléfonos |

### 3.2 Decisiones de interfaz

- **Primero el celular** (RF-17, RNF-01): menú inferior en el celular y lateral en el PC; probado desde 360 px.
- **Rutas por rol** en `App.jsx`. Es solo comodidad para el usuario: la seguridad real está en el backend.
- **El servidor decide qué acciones se pueden hacer.** El detalle de la orden trae `transiciones`, `puede_asignar`, `puede_editar_trabajo` y `puede_editar_recepcion`, y la interfaz solo muestra esos botones. Así las reglas no se duplican en el navegador.
- **Accesibilidad** (RNF-07): etiquetas en todos los campos, `aria-live` en búsquedas, enlace «Saltar al contenido», diálogos con `<dialog>` nativo y estados con texto e ícono, no solo con color.
- **Sin librerías extra** para formularios ni para solicitudes HTTP (ADR-004).
- **Vista de la orden en una columna** (O-1): encabezado, estado, acciones (con el informe PDF), información general, diagnóstico, trabajo realizado, costos, enlace e historial. Diagnóstico y trabajo comparten un solo borrador: «Guardar» en cualquiera envía los dos.
- **Terminología** (T-1): la interfaz dice «Cliente», no «Dueño», para la persona registrada con el vehículo. El API y la base no cambian (`cliente_id`).
- **Fondos por módulo** (T-2, T-3): `FondoModulo` elige la escena por el prefijo de la ruta y la pinta en una capa fija detrás del contenido (`-z-10` dentro de un contenedor `isolate`), con opacidad 0,5, máscara de degradado y fundido de 500 ms al cambiar de módulo. Es `aria-hidden` y no recibe clics.
- En desarrollo, Vite reenvía `/api` a `http://localhost:8000`, así que la interfaz y la API comparten origen igual que en producción y la cookie funciona sin CORS.

---

## 4. PostgreSQL

### 4.1 Modelo

Son **12 tablas** (más `alembic_version`) y cuatro tipos enumerados (`rol_usuario`, `estado_orden`, `tipo_movimiento` y `tipo_vehiculo`). Las *tablas raíz* llevan `taller_id`; las *tablas hijas* heredan el taller de su tabla padre. Las migraciones 0006 y 0007 agregaron columnas, no tablas.

```mermaid
erDiagram
    TALLER ||--o{ USUARIO : emplea
    TALLER ||--o{ CLIENTE : atiende
    TALLER ||--o{ VEHICULO : registra
    TALLER ||--o{ ORDEN_TRABAJO : gestiona
    TALLER ||--o{ REPUESTO : almacena
    TALLER ||--o{ SERVICIO : ofrece
    CLIENTE ||--o{ VEHICULO : "cliente actual"
    CLIENTE ||--o{ ORDEN_TRABAJO : "cliente al momento"
    VEHICULO ||--o{ ORDEN_TRABAJO : recibe
    USUARIO |o--o{ ORDEN_TRABAJO : "mecánico asignado"
    USUARIO |o--o{ CLIENTE : anonimiza
    ORDEN_TRABAJO ||--|{ HISTORIAL_ESTADO_ORDEN : registra
    ORDEN_TRABAJO ||--o{ ASIGNACION_ORDEN : registra
    ORDEN_TRABAJO ||--o{ ORDEN_SERVICIO : "mano de obra"
    ORDEN_TRABAJO ||--o{ ORDEN_REPUESTO : consume
    SERVICIO |o--o{ ORDEN_SERVICIO : referencia
    REPUESTO ||--o{ ORDEN_REPUESTO : "usado en"
    REPUESTO ||--o{ MOVIMIENTO_INVENTARIO : tiene
    ORDEN_TRABAJO |o--o{ MOVIMIENTO_INVENTARIO : origina
```

El detalle de cada atributo está en [docs/modelo-datos.md](../modelo-datos.md) y en [modelo-datos.dbml](../modelo-datos.dbml).

### 4.2 Restricciones que garantiza la base de datos

| Regla | Mecanismo |
|---|---|
| Stock nunca negativo (RN-02) | `CHECK repuesto.stock_actual >= 0` + `SELECT … FOR UPDATE` en el servicio |
| Una sola orden abierta por vehículo (RN-08) | Índice único parcial `uq_orden_vehiculo_abierta` |
| Consecutivo de orden por taller (RN-12) | Bloqueo de la fila del taller + UQ `(taller_id, numero)` |
| Placa única por taller | UQ `(taller_id, placa)` |
| Documento único por taller cuando existe | Índice único parcial `uq_cliente_taller_documento` |
| Autorización de datos (RN-10) | `CHECK autoriza_datos = true` |
| Motivo al cancelar (RN-18) | `CHECK (estado <> 'CANCELADA' OR motivo_cancelacion IS NOT NULL)` |
| Fecha de entrega al entregar | `CHECK (estado <> 'ENTREGADO' OR fecha_entrega IS NOT NULL)` |
| Anonimización coherente y auditada (RN-11, A-7) | `CHECK ck_cliente_anonimizacion_coherente` |
| El detalle de «Otro» solo existe con la categoría «Otro» (O-5) | `CHECK ck_orden_trabajo_categoria_otro_solo_con_otro` |
| Todo vehículo es carro o moto (V-1) | Columna `vehiculo.tipo` de tipo `tipo_vehiculo`, `NOT NULL`, por defecto `CARRO` |
| La historia no se borra (RN-11) | Todas las FK con `ON DELETE RESTRICT` |
| Montos exactos (RN-19) | `NUMERIC(12,2)` para dinero, `NUMERIC(10,2)` para cantidades |

Los nombres de las restricciones siguen una convención fija (`core/db.py`), por ejemplo `uq_vehiculo_taller_placa` o `ck_repuesto_stock_no_negativo`. Así los errores de integridad se pueden traducir a mensajes del taller.

### 4.3 Bases del entorno local

| Base | Uso |
|---|---|
| `taller_dev` | Desarrollo y demostración (con la semilla de datos ficticios) |
| `taller_test` | Exclusiva de `pytest`: se migra desde cero, **se vacía en cada prueba** y se revierte al final |

Las pruebas corren contra PostgreSQL real, **nunca contra SQLite**, para probar las mismas restricciones, bloqueos e índices parciales que en producción.

---

## 5. SQLAlchemy

- **Versión 2** con estilo tipado (`Mapped[...]`, `mapped_column`) y consultas `select()`.
- **Sesión por solicitud** (`core/db.py`, `obtener_db`); `expire_on_commit=False`.
- **Conexión robusta:** `pool_pre_ping=True` y `connect_timeout=10` evitan solicitudes colgadas si la base gratuita está «dormida».
- **Solo consultas parametrizadas.** Nunca se arma SQL concatenando texto (SPEC §16).
- **Bloqueos pesimistas** (`with_for_update`) en las operaciones con concurrencia:

| Operación | Fila bloqueada | Motivo |
|---|---|---|
| Abrir orden | `taller` | Consecutivo sin huecos ni repetidos (RN-12) |
| Cambiar estado, asignar o registrar líneas | `orden_trabajo` | Dos cambios simultáneos no se pisan |
| Movimiento de stock | `repuesto` | El stock nunca queda negativo (RN-02) |
| Anonimizar | `cliente` | Nadie lo edita ni le abre una orden al mismo tiempo |

**Detalle aprendido:** PostgreSQL no permite `FOR UPDATE` sobre el lado opcional de un `LEFT OUTER JOIN`. Por eso las consultas con bloqueo no se combinan con `joinedload` de relaciones que pueden ser nulas (por ejemplo, el mecánico de una orden).

---

## 6. Alembic

| Migración | Fecha | Contenido |
|---|---|---|
| `0001_taller_y_usuario` | 23/10/2026 | `taller`, `usuario`, tipo `rol_usuario` |
| `0002_cliente_y_vehiculo` | 25/10/2026 | `cliente` (autorización obligatoria), `vehiculo` (placa única por taller) |
| `0003_orden_historial_asignacion` | 25/10/2026 | `orden_trabajo`, `historial_estado_orden`, `asignacion_orden`, tipo `estado_orden`, índice de orden abierta |
| `0004_inventario_y_lineas_orden` | 26/10/2026 | `servicio`, `repuesto`, `orden_servicio`, `orden_repuesto`, `movimiento_inventario`, tipo `tipo_movimiento` |
| `0005_auditoria_anonimizacion` | 28/10/2026 | `cliente.anonimizado_en`, `cliente.anonimizado_por` y el CHECK de coherencia |
| `0006_tipo_vehiculo` | 04/11/2026 | Tipo `tipo_vehiculo` (`CARRO`, `MOTO`) y columna `vehiculo.tipo`; los vehículos existentes quedan como `CARRO` (V-1) |
| `0007_categoria_problema` | 04/11/2026 | `orden_trabajo.categoria_problema` (varchar 80), `categoria_otro` (varchar 120), `observacion_cliente` (text) y el CHECK de «Otro». Copia `motivo_ingreso` a `observacion_cliente` en las órdenes anteriores, que quedan sin categoría (O-6) |

**Comandos** (en `backend/`):

```
uv run alembic upgrade head      # aplica todas las migraciones
uv run alembic current           # muestra la versión actual
uv run alembic downgrade -1      # revierte la última
```

Cada migración tiene `downgrade`. La suite de pruebas ejecuta `downgrade base` y `upgrade head` al empezar, así que **las migraciones se prueban en cada ejecución**.

---

## 7. Variables de entorno

La configuración se lee **solo de variables de entorno** (RNF-10, `core/config.py`, `pydantic-settings`). En local se toman de `backend/.env`, que **nunca se sube al repositorio**. La plantilla es `backend/.env.example`.

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `DATABASE_URL` | Sí | — | Conexión a PostgreSQL, por ejemplo `postgresql+psycopg://usuario:clave@host:5432/taller_dev` |
| `SECRET_KEY` | Sí | — | Firma de los tokens de sesión. **Mínimo 32 caracteres**; si es más corta, la aplicación no arranca |
| `ENTORNO` | No | `desarrollo` | `desarrollo` o `produccion`. En producción la cookie exige HTTPS (`Secure`) |
| `SESION_HORAS` | No | `8` | Duración de la sesión, entre 1 y 24 horas |
| `ORIGEN_PUBLICO` | No | `http://localhost:5173` | Declarada para la URL pública. **El código actual no la usa**: el enlace de seguimiento se arma en el navegador con el dominio desde el que se abre el sistema |
| `TEST_DATABASE_URL` | Solo para pruebas | — | Base exclusiva de `pytest`. **No apuntarla a la base de desarrollo**: se vacía |
| `CLAVE_ADMIN` | No | — | Solo para `crear_taller`; evita que el script pida la clave por teclado (útil en automatización) |

Para generar una `SECRET_KEY`:

```
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 8. Estructura del proyecto

```
mi-prototipo/
├── SPEC.md                         Especificación oficial (requisitos, reglas, decisiones)
├── README.md                       Puesta en marcha local
├── docs/
│   ├── decisions/                  ADR-001 … ADR-006
│   ├── modelo-datos.md / .dbml     Modelo entidad-relación
│   ├── historial-commits.md        Hitos del desarrollo
│   ├── guia-skills-diseno.md       Guía de las skills de diseño usadas en el rediseño
│   └── sustentacion/               Esta documentación
├── backend/
│   ├── pyproject.toml, uv.lock     Dependencias (uv)
│   ├── alembic.ini, alembic/       Migraciones 0001–0007
│   ├── app/
│   │   ├── main.py                 Creación de la app, middleware, frontend estático
│   │   ├── api/                    Rutas: auth, usuarios, clientes, vehiculos, ordenes,
│   │   │                           mecanicos, repuestos, dashboard, seguimiento, catalogos,
│   │   │                           salud, deps
│   │   ├── schemas/                Contratos Pydantic de entrada y salida
│   │   ├── services/               Reglas de negocio (flujo_orden, ordenes, inventario,
│   │   │                           lineas_orden, liquidacion, seguimiento, clientes,
│   │   │                           vehiculos, categorias, informe_pdf…)
│   │   ├── models/                 Tablas SQLAlchemy
│   │   ├── core/                   config, db, seguridad, errores, limites
│   │   └── scripts/                crear_taller, semilla_demo
│   └── tests/                      16 archivos, 263 pruebas pytest
├── frontend/
│   ├── package.json, vite.config.js, eslint.config.js
│   └── src/                        pages/, components/, components/orden/, assets/fondos/,
│                                   sesion/, hooks/, api/
└── investigacion_completa.md, entrevistas_e_instrumentos.md, resumen_requerimientos.md
                                    Documentos de la tesis (D1, D2, D3)
```

### 8.1 Puesta en marcha local (resumen)

```
# Backend
cd backend
cp .env.example .env               # completar DATABASE_URL, TEST_DATABASE_URL y SECRET_KEY
uv sync
uv run alembic upgrade head
uv run python -m app.scripts.semilla_demo     # opcional: datos ficticios
uv run uvicorn app.main:app --reload          # http://localhost:8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev                                   # http://localhost:5173
```

**Calidad:** `uv run pytest`, `uv run ruff check .`, `uv run ruff format .`, `npm run lint`, `npm run build`.

---

## 9. Flujo de autenticación

Diseño de [ADR-005](../decisions/ADR-005-autenticacion.md): **JWT firmado (HS256) dentro de una cookie `httpOnly`**, sin guardar nada en `localStorage`. El usuario **se vuelve a leer de la base en cada solicitud**.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant F as React (navegador)
    participant A as FastAPI /auth
    participant S as services/auth.py
    participant D as PostgreSQL

    U->>F: Correo y clave
    F->>A: POST /api/v1/auth/login (JSON)
    A->>S: autenticar(email, clave)
    S->>D: SELECT usuario WHERE email = lower(email)
    D-->>S: usuario (o ninguno)
    Note over S: verifica argon2id; si el correo no existe,<br/>verifica contra un hash ficticio (mismo tiempo)
    alt credenciales válidas, usuario y taller activos
        S->>D: UPDATE ultimo_acceso
        A-->>F: 200 {usuario, taller} + Set-Cookie: sesion=JWT<br/>(HttpOnly, SameSite=Lax, Secure en producción, 8 h)
    else cualquier fallo
        A-->>F: 401 "Correo o clave incorrectos"
    end

    U->>F: Usa el sistema
    F->>A: GET /api/v1/ordenes (cookie automática)
    Note over A: deps.obtener_usuario_actual:<br/>valida firma y vencimiento del JWT
    A->>D: SELECT usuario por id (en cada solicitud)
    alt usuario activo y taller activo
        Note over A: requiere_roles(...) lee el rol de la base
        A-->>F: 200 datos filtrados por taller_id
    else desactivado o token inválido
        A-->>F: 401 "Su sesión no es válida…"
    end
```

**Decisiones de seguridad:**

| Medida | Para qué |
|---|---|
| Cookie `httpOnly` | Un script malicioso en la página no puede leer el token |
| `SameSite=Lax` + JSON obligatorio en las modificaciones (415) | Defensa contra CSRF |
| `Secure` cuando `ENTORNO=produccion` | La cookie solo viaja por HTTPS |
| Mensaje genérico y tiempo igual con un hash ficticio | No revela qué correos existen |
| El usuario y su rol se releen de la base en cada solicitud | Desactivar o cambiar el rol tiene efecto inmediato; el rol nunca sale del token ni del cliente |
| argon2id | Hash de claves resistente a ataques por fuerza bruta con GPU |
| Vencimiento de 8 h (configurable) | Limita el uso de una sesión olvidada |

**Pendiente (Semana 5):** límite de intentos de inicio de sesión, cabeceras de seguridad (CSP, HSTS, etc.) y cambio y recuperación de clave.

---

## 10. Multi-tenant (varios talleres)

Diseño de [ADR-006](../decisions/ADR-006-multi-tenant.md): **una base de datos y un esquema compartidos**, con aislamiento lógico por `taller_id`.

```mermaid
flowchart TD
    R["Solicitud autenticada"] --> U["deps.obtener_usuario_actual<br/>(usuario releído de la base)"]
    U --> T["taller_id = usuario.taller_id<br/>(nunca del cuerpo, la URL ni los parámetros)"]
    T --> S["Servicio: toda consulta incluye<br/>WHERE taller_id = :taller_id"]
    S --> Q{"¿El recurso es<br/>de ese taller?"}
    Q -- "Sí" --> OK["200 con los datos"]
    Q -- "No, o no existe" --> NF["404 «no existe»<br/>(no distingue entre los dos casos)"]
    S --> H["Tablas hijas (historial, líneas, movimientos):<br/>se llega siempre a través de la orden o el repuesto<br/>ya filtrado por taller"]
```

**Reglas de implementación:**

1. El `taller_id` sale **siempre** del usuario de la sesión.
2. Las **referencias cruzadas** también se validan: al crear un carro con `cliente_id`, o una orden con `vehiculo_id` y `mecanico_id`, se comprueba que esos registros sean del mismo taller.
3. Las restricciones de unicidad son **por taller**: placa, número de orden, código de repuesto y documento del cliente. Solo hay dos excepciones globales: el correo del usuario (el login no pide el taller) y el código de seguimiento (el enlace no lleva el taller).
4. **Cada recurso tiene pruebas de aislamiento** (RNF-05): un usuario del taller A intenta leer o modificar datos del taller B y recibe 404, y los listados y el dashboard solo cuentan lo propio.

La semilla de demostración crea **dos talleres con un carro de placa `ABC123` cada uno** y un repuesto `W712` en cada catálogo, a propósito, para comprobar el aislamiento a mano.

---

## 11. Inventario

### 11.1 Modelo

- `repuesto`: catálogo por taller, con `stock_actual`, `stock_minimo`, `precio_venta`, `unidad` y `activo`.
- `movimiento_inventario`: libro de solo inserción, con el tipo (`ENTRADA`, `SALIDA`, `AJUSTE`, `DEVOLUCION`), la cantidad con signo, el `stock_resultante`, el usuario, la orden si aplica y la nota. Un CHECK compuesto asegura que el signo coincida con el tipo.
- `orden_repuesto`: línea de la orden con la cantidad, una **copia del precio** (RN-05) y quién la registró.

### 11.2 Registrar un repuesto en una orden (RN-02, RN-05, RN-15)

```mermaid
sequenceDiagram
    autonumber
    participant F as React
    participant A as POST /ordenes/{id}/repuestos
    participant L as services/lineas_orden.py
    participant I as services/inventario.py
    participant D as PostgreSQL

    F->>A: {repuesto_id, cantidad}
    A->>L: agregar_repuesto(...)
    L->>D: SELECT orden ... FOR UPDATE (filtrada por taller)
    Note over L: la orden debe estar abierta (RN-07)<br/>y el usuario autorizado (asignado, recepción o admin)
    L->>I: descontar_para_orden(...) → _mover_stock(SALIDA)
    I->>D: SELECT repuesto ... FOR UPDATE
    alt stock suficiente
        I->>D: UPDATE repuesto.stock_actual<br/>INSERT movimiento_inventario (SALIDA, stock_resultante)
        L->>D: INSERT orden_repuesto (precio copiado, registrado_por)
        D-->>A: COMMIT (todo o nada)
        A-->>F: 201 orden con la liquidación recalculada
    else no alcanza
        A-->>F: 409 «No hay suficiente …: quedan N»
    end
```

- **Una sola transacción:** el descuento, el movimiento y la línea se guardan juntos o no se guarda nada.
- **Quitar la línea** o **cancelar la orden** genera movimientos `DEVOLUCION` (`devolver_a_stock`, RN-03).
- **Ajuste por conteo** (S4-1): el usuario envía la cantidad contada y el servidor calcula la diferencia.
- **Alerta** (RN-04): un repuesto está «bajo» cuando `stock_actual <= stock_minimo`. El dashboard las ordena por urgencia.
- **Concurrencia probada:** `test_concurrencia_stock.py` lanza registros simultáneos que, juntos, superan el stock, y verifica que nunca quede negativo.

### 11.3 Liquidación (RN-06)

`services/liquidacion.py` calcula en el servidor:

```
mano_de_obra = Σ (cantidad × precio_unitario) de orden_servicio
repuestos    = Σ (cantidad × precio_unitario) de orden_repuesto
total        = mano_de_obra + repuestos          (sin IVA, P-9)
```

Usa `Decimal`; cada subtotal se redondea al centavo con `ROUND_HALF_UP`. **No se guarda un total** ni se acepta un total enviado por el navegador.

---

## 12. Seguimiento público

Diseño de [ADR-005](../decisions/ADR-005-autenticacion.md) y RF-13.

- Al abrir la orden se genera `codigo_seguimiento = secrets.token_urlsafe(16)`: **128 bits aleatorios**, 22 caracteres, único en todo el sistema (RN-12).
- La ruta pública de la interfaz es `/seguimiento/:codigo` y consume `GET /api/v1/seguimiento/{codigo}`, **sin sesión**.
- Solo se consulta la base si el código tiene el formato esperado (`[A-Za-z0-9_-]{16,43}`). Un código inválido o inexistente responde 404 con «No encontramos esta orden. Revise el enlace que le enviaron.»
- **Límite:** 30 consultas por minuto por IP, con ventana deslizante en memoria (`core/limites.py`). Si se supera: 429 «Demasiadas consultas seguidas. Espere un minuto.»
- **Lista blanca de campos:** el esquema `SeguimientoSalida` solo declara el taller, el número, la placa enmascarada (`ABC***`), la marca, el modelo, el estado, las etapas con fecha, las líneas de mano de obra y repuestos, y la liquidación. **Lo que no está declarado no sale.** No hay datos del cliente, notas internas, kilometraje, motivo de ingreso ni nombres de usuarios. `test_seguimiento.py` lo verifica buscando esos datos en la respuesta.

```mermaid
sequenceDiagram
    actor C as Cliente (sin cuenta)
    participant P as Página /seguimiento/:codigo
    participant A as GET /api/v1/seguimiento/{codigo}
    participant L as LimitadorSolicitudes (30/min/IP)
    participant S as services/seguimiento.py
    participant D as PostgreSQL

    C->>P: Abre el enlace recibido por WhatsApp
    P->>A: GET (sin cookie)
    A->>L: permitir(ip)
    alt más de 30 en el último minuto
        A-->>P: 429
    else permitido
        A->>S: obtener_por_codigo(codigo)
        S->>D: SELECT orden WHERE codigo_seguimiento = :codigo
        alt existe
            A-->>P: 200 SeguimientoSalida (sin datos personales)
        else no existe o formato inválido
            A-->>P: 404
        end
    end
```

**Informe PDF público** (`GET /seguimiento/{codigo}/informe.pdf`, O-3): usa el mismo limitador y la misma validación del código. Solo existe si la orden está `ENTREGADO`. Omite el nombre y el teléfono del cliente y el kilometraje, y enmascara la placa. Como excepción aprobada por el autor, sí incluye la categoría, la observación, el diagnóstico y el trabajo realizado, que el JSON de seguimiento no expone (sección 13).

**Limitaciones conocidas:**
- El límite está **en memoria**: sirve con una sola instancia, que es el caso del plan gratuito. Con varias instancias habría que llevar el contador a un almacén compartido.
- Detrás del proxy del hosting, `request.client.host` sería la IP del proxy. **Ajustarlo es tarea de la Semana 5** (S4-8).
- El enlace **no vence** mientras exista la orden (S4-6).

---

## 13. Informe PDF final (decisiones O-2 a O-4)

- **Dónde:** `services/informe_pdf.py`, con **fpdf2**. Se eligió generarlo en el servidor, y no en el navegador, para que la regla «solo `ENTREGADO`» la valide el backend y quede cubierta por pytest.
- **Regla:** `generar()` lanza `Conflicto` (409, «El informe PDF solo está disponible cuando la orden fue entregada») si la orden no está `ENTREGADO`, incluida `CANCELADA`.
- **Dos variantes con el mismo código:**

| Dato | Interno (`publico=False`) | Público (`publico=True`) |
|---|---|---|
| Taller, número, fechas de ingreso y entrega | Sí | Sí |
| Nombre y teléfono del cliente | Sí | No («Datos personales protegidos (Ley 1581 de 2012)») |
| Placa | Completa | Enmascarada (`ABC***`) |
| Tipo, marca, modelo y color | Sí | Sí |
| Kilometraje | Sí | No |
| Categoría, observación, diagnóstico y trabajo | Sí | Sí (excepción O-3) |
| Mano de obra, repuestos y total | Sí | Sí |
| Historial de estados | Sin notas internas ni nombres de usuarios | Igual |

- **Permisos del interno:** cualquier usuario que pueda ver la orden; el mecánico solo las suyas (otro mecánico recibe 404, como cualquier recurso ajeno; sin sesión, 401).
- **Fuente:** Helvetica, la fuente base del formato PDF (Latin-1). Los caracteres que no caben (emoji, comillas tipográficas) se reemplazan, y la prueba `test_textos_fuera_de_latin1_no_rompen_el_pdf` lo verifica.
- **Formato:** carta; pesos con punto de miles; fechas en hora de Colombia (UTC−5). El archivo se llama `informe-orden-{numero}.pdf`.

## 14. Categoría del problema (decisiones O-5 a O-7)

- **Catálogo fijo en código:** `services/categorias.py` define **22 categorías para carro y 20 para moto**; cada lista termina en «Otro». Se sirve en `GET /catalogos/categorias-problema`.
- **Se guarda el nombre**, no un código: si el catálogo cambia, las órdenes y sus PDF no cambian.
- **Validación en el servidor:** la categoría debe ser del tipo del vehículo; «Otro» exige `categoria_otro`, y el CHECK de la base impide `categoria_otro` con otra categoría. El mecánico recibe 403 si intenta registrar o corregir el problema.
- **Compatibilidad (O-6):** `motivo_ingreso` sigue siendo `NOT NULL` y se compone como «categoría — observación». El API acepta todavía solo `motivo_ingreso` (forma anterior); sin categoría ni motivo responde 422.
- **Búsqueda (O-7):** en el navegador (`src/problema.js`) se normalizan tildes y mayúsculas; Enter elige la primera coincidencia; la lista cambia con el tipo del vehículo.

## 15. Alta de cliente con vehículo (decisiones O-8 y O-9)

- `POST /clientes` acepta un objeto `vehiculo` opcional. `services/clientes.crear()` arma el cliente y, si llega el vehículo, lo crea con `services/vehiculos.py` asociado al mismo objeto `Cliente`; los dos se guardan con **un solo commit**. Si la placa existe (violación de `uq_vehiculo_taller_placa`) o un dato falla, se revierte todo y el error llega con el campo `vehiculo.<campo>`.
- La respuesta es el detalle del cliente con sus vehículos; amplía la respuesta anterior sin quitar campos.
- La interfaz usa el mismo componente `CamposVehiculo` en el alta del cliente y en el formulario del vehículo, así que las validaciones y los textos son iguales en los dos lugares.

## 16. Interfaz: rediseño, tipo de vehículo y fondos (decisiones V-1 a V-5 y T-1 a T-3)

- **Tipo de vehículo:** `FiltroTipoVehiculo` envía `tipo` al API; el filtro se combina con la búsqueda por placa y con «Incluir inactivos». `EtiquetaTipo` muestra ícono y texto (RNF-07).
- **Rediseño (V-4):** logo, inicio de sesión ilustrado, navegación lateral oscura, botones con estados de foco, presión y carga, y tokens de color en `src/index.css` (`@theme` de Tailwind 4). Las animaciones duran entre 150 y 500 ms y se apagan con «reducir movimiento».
- **Fondos (T-2, T-3):** seis SVG de línea en `src/assets/fondos/`, de menos de 2,5 KB cada uno. Vite los incrusta en el código, así que no generan solicitudes extra. Comparten trazo, la tinta `#115e59` y el mismo dibujo del carro de `IlustracionTaller`.
- **Limitación conocida de los fondos:** con opacidad 0,5, un texto gris (`texto-suave`) que quede justo sobre una línea de la escena baja a un contraste de ~3:1, por debajo del 4,5:1 de RNF-07. Las tarjetas, listas y formularios son opacos y no se ven afectados; la máscara deja limpias las zonas de títulos. Ver SPEC §21.11.

---

## 17. Pruebas automatizadas

| Archivo | Funciones | Casos | Qué cubre |
|---|---|---|---|
| `test_auth.py` | 13 | 13 | Login, cookie, mensaje genérico, argon2id, token alterado, desactivación inmediata, 415 sin JSON, formato de error |
| `test_usuarios.py` | 10 | 12 | Alta, correo duplicado, clave corta, solo ADMIN, aislamiento, no quitarse el propio acceso |
| `test_clientes.py` | 17 | 21 | RN-10 (API y CHECK), normalización, documento único, búsqueda, permisos, aislamiento |
| `test_cliente_con_vehiculo.py` | 6 | 6 | O-8: alta conjunta, sin vehículo, placa repetida sin guardar nada, error con su campo, permisos, más vehículos desde la ficha |
| `test_vehiculos.py` | 24 | 35 | RN-20, placa única, cambio de cliente, S2-4, aislamiento; V-1 y V-2: tipo por defecto, moto, tipo inválido, no vaciarlo, filtro combinado y aislado |
| `test_flujo_orden.py` | 9 | 22 | Máquina de estados pura, H-1, RN-07, RN-18 |
| `test_ordenes.py` | 30 | 36 | RF-05 a RF-07, RF-11, RN-08, RN-12, RN-13, RN-16, RN-17, RN-18, Mis órdenes, aislamiento |
| `test_categoria_problema.py` | 14 | 17 | O-5 a O-7: catálogo por tipo, búsqueda sin tildes, «Otro», forma anterior, corrección, órdenes antiguas, 403 del mecánico |
| `test_concurrencia_ordenes.py` | 2 | 2 | Consecutivo y orden abierta única con recepciones simultáneas |
| `test_inventario.py` | 19 | 26 | RF-08, RF-10, entradas, ajustes, RN-02, RN-04 |
| `test_concurrencia_stock.py` | 1 | 1 | Stock nunca negativo con registros simultáneos |
| `test_liquidacion.py` | 19 | 24 | RF-09, RF-12, RN-03, RN-05, RN-06, RN-07, RN-15 |
| `test_informe_pdf.py` | 12 | 16 | O-2 a O-4: informe interno y público, permisos, 409 antes de entregar y en canceladas, sin datos personales, cliente anonimizado, órdenes antiguas, Latin-1, formato de pesos |
| `test_dashboard.py` | 4 | 4 | Conteos, alertas, aislamiento, rol |
| `test_seguimiento.py` | 5 | 8 | Acceso sin sesión, sin datos personales, código inválido, límite |
| `test_anonimizacion.py` | 15 | 20 | RN-11: datos borrados, auditoría, conservación, permisos, confirmación, A-1, A-4, CHECK |
| **Total** | **200** | **263** | Algunas pruebas son parametrizadas |

```
cd backend
uv run pytest          # 263 passed (≈ 110 s en el equipo de desarrollo)
```

**Cobertura del backend** (medida el 05/11/2026 con `pytest-cov` en un entorno temporal, sin agregarlo a las dependencias):

```
uv run --with pytest-cov pytest --cov=app
```

| Alcance | Sentencias | Cobertura |
|---|---|---|
| Todo `app/` | 2.144 | **91 %** |
| `app/` sin los scripts de consola (`crear_taller`, `semilla_demo`, que no tienen pruebas) | 2.001 | **97 %** |
| `services/informe_pdf.py`, `services/categorias.py`, `services/flujo_orden.py`, `services/liquidacion.py` | — | 100 % |

El frontend **no tiene pruebas automatizadas** (SPEC §15): se verifica con la lista manual por pantalla, `npm run lint` y `npm run build`.

---

## 18. Cambios desde la versión documentada anterior (`84f20f3`, 28/10/2026)

| Commit | Fecha | Cambio | Migración | Pruebas |
|---|---|---|---|---|
| `e4a164a` | 28/10/2026 | Documentación de sustentación | — | 214 |
| `e4692f8` | 28/10/2026 | Historial de commits | — | 214 |
| `2faf3c0` | 03/11/2026 | Skills de diseño y su guía (solo documentación y herramientas) | — | 214 |
| `e3fc487` | 04/11/2026 | Rediseño visual y tipo de vehículo CARRO/MOTO (V-1 a V-5) | 0006 | 224 |
| `e51d187` | 04/11/2026 | Vista vertical de la orden, informe PDF con fpdf2, categoría del problema y observación, alta de cliente con vehículo (O-1 a O-9) | 0007 | 263 |
| `464e261` | 04/11/2026 | Registro de la aprobación de O-1 a O-9 | — | 263 |
| Sin commit | 05/11/2026 | Terminología «Cliente» en lugar de «Dueño» (T-1) y fondos temáticos por módulo (T-2, T-3) | — | 263 |
