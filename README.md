# Taller Digital

Prototipo web (MVP) para gestionar los procesos operativos de talleres mecánicos de la zona norte de Cali: clientes, vehículos, órdenes de trabajo, inventario, liquidación y seguimiento para el cliente.

Proyecto de grado de Ingeniería de Software, Corporación Universitaria Iberoamericana.

- **Qué se construye y por qué:** [SPEC.md](SPEC.md)
- **Decisiones técnicas:** [docs/decisions/](docs/decisions/)
- **Modelo de datos:** [docs/modelo-datos.md](docs/modelo-datos.md)

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13 · FastAPI · SQLAlchemy 2 · Alembic |
| Base de datos | PostgreSQL 17 |
| Frontend | React · Vite · Tailwind CSS · React Router |

## Requisitos

| Software | Versión | Para qué |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | reciente | Instala Python 3.13 y las dependencias del backend |
| Node.js | 24 LTS | Frontend |
| PostgreSQL | 17 | Base de datos |
| Git | 2.x | Control de versiones |

## Puesta en marcha (local)

### 1. Base de datos

Con PostgreSQL instalado, cree dos bases: una para trabajar y otra solo para las pruebas automatizadas.

```
psql -U postgres -c "CREATE DATABASE taller_dev;"
psql -U postgres -c "CREATE DATABASE taller_test;"
```

### 2. Backend

```
cd backend
copy .env.example .env      # en Linux o Mac: cp .env.example .env
```

Abra `backend/.env` y complete estos valores:
- `DATABASE_URL` y `TEST_DATABASE_URL`, con la clave de su usuario `postgres`.
- `SECRET_KEY`, generada con:
  ```
  uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```

Luego:

```
uv sync                                   # instala dependencias
uv run alembic upgrade head               # crea las tablas
uv run python -m app.scripts.semilla_demo # (opcional) datos ficticios de demostración
uv run uvicorn app.main:app --reload      # API en http://localhost:8000
```

La documentación interactiva de la API queda en http://localhost:8000/api/docs.

Para crear un taller real con su administrador:

```
uv run python -m app.scripts.crear_taller --taller "Nombre del taller" --nombre "Nombre Admin" --email admin@correo.co
```

### 3. Frontend

En otra terminal:

```
cd frontend
npm install
npm run dev                               # interfaz en http://localhost:5173
```

En desarrollo, Vite reenvía `/api` al backend, así que la cookie de sesión funciona sin configuración adicional.

### Usuarios de demostración

Los crea `semilla_demo`. La clave de todos es `demo12345`.

| Taller | Correo | Rol |
|---|---|---|
| Taller Demo Norte | admin@norte.demo.co | Administrador |
| Taller Demo Norte | recepcion@norte.demo.co | Recepción |
| Taller Demo Norte | mecanico@norte.demo.co | Mecánico |
| Taller Demo Chipichape | admin@chipichape.demo.co | Administrador |
| Taller Demo Chipichape | mecanico@chipichape.demo.co | Mecánico |

## Comandos

| Comando (en `backend/`) | Qué hace |
|---|---|
| `uv run pytest` | Pruebas automatizadas (usan `TEST_DATABASE_URL`, que se vacía en cada ejecución) |
| `uv run ruff check . && uv run ruff format .` | Revisión de estilo y formato |
| `uv run alembic upgrade head` | Aplica las migraciones |

| Comando (en `frontend/`) | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run lint` | Revisión de estilo |
| `npm run build` | Compila la interfaz en `frontend/dist`. El backend la sirve automáticamente si existe. |

## Arquitectura en una línea

Monolito cliente-servidor por capas: API → servicios (reglas de negocio y filtro por taller) → acceso a datos → PostgreSQL. React consume la API desde el mismo dominio. Ver [ADR-001](docs/decisions/ADR-001-arquitectura.md).
