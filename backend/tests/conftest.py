"""Las pruebas corren contra un PostgreSQL de prueba, nunca contra SQLite (ADR-002).

La base se toma de TEST_DATABASE_URL (variable de entorno o backend/.env) y se
vacía en cada prueba: no apunte esta variable a la base de desarrollo.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import dotenv_values

DIRECTORIO_BACKEND = Path(__file__).resolve().parents[1]
_valores_env = dotenv_values(DIRECTORIO_BACKEND / ".env")
URL_PRUEBAS = os.environ.get("TEST_DATABASE_URL") or _valores_env.get("TEST_DATABASE_URL")
if not URL_PRUEBAS:
    raise RuntimeError("Defina TEST_DATABASE_URL en backend/.env para ejecutar las pruebas")

# Debe configurarse antes de importar la aplicación, que crea el motor al cargar.
os.environ["DATABASE_URL"] = URL_PRUEBAS
os.environ["SECRET_KEY"] = "clave-exclusiva-para-pruebas-automatizadas-0123456789"
os.environ["ENTORNO"] = "desarrollo"

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import SesionLocal, motor  # noqa: E402
from app.core.seguridad import hashear_clave  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Cliente, RolUsuario, Taller, Usuario, Vehiculo  # noqa: E402

CLAVE = "clave-segura-1"
# Hijas antes que padres; CASCADE cubre una tabla nueva que se olvide agregar aquí.
TABLAS = [
    "asignacion_orden",
    "historial_estado_orden",
    "orden_trabajo",
    "vehiculo",
    "cliente",
    "usuario",
    "taller",
]


@pytest.fixture(scope="session", autouse=True)
def esquema():
    """Aplica las migraciones reales (así también se prueban) y las revierte al final."""
    config = Config(str(DIRECTORIO_BACKEND / "alembic.ini"))
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield
    motor.dispose()
    command.downgrade(config, "base")


@pytest.fixture(autouse=True)
def limpiar_tablas():
    yield
    with motor.begin() as conexion:
        conexion.execute(text(f"TRUNCATE {', '.join(TABLAS)} RESTART IDENTITY CASCADE"))


@pytest.fixture
def db():
    with SesionLocal() as sesion:
        yield sesion


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def crear_usuario(db):
    def _crear(
        taller: Taller,
        email: str,
        rol: RolUsuario = RolUsuario.ADMIN,
        activo: bool = True,
        clave: str = CLAVE,
    ) -> Usuario:
        usuario = Usuario(
            taller_id=taller.id,
            nombre=email.split("@")[0].title(),
            email=email,
            password_hash=hashear_clave(clave),
            rol=rol,
            activo=activo,
        )
        db.add(usuario)
        db.commit()
        return usuario

    return _crear


@pytest.fixture
def taller_a(db) -> Taller:
    taller = Taller(nombre="Taller A")
    db.add(taller)
    db.commit()
    return taller


@pytest.fixture
def taller_b(db) -> Taller:
    taller = Taller(nombre="Taller B")
    db.add(taller)
    db.commit()
    return taller


@pytest.fixture
def crear_cliente(db):
    """Crea el cliente directamente en la base, sin pasar por la API."""

    def _crear(taller: Taller, nombre: str = "Ana Gómez", **campos) -> Cliente:
        cliente = Cliente(
            taller_id=taller.id,
            nombre=nombre,
            telefono=campos.pop("telefono", "3001234567"),
            autoriza_datos=True,
            fecha_autorizacion=datetime.now(UTC),
            **campos,
        )
        db.add(cliente)
        db.commit()
        return cliente

    return _crear


@pytest.fixture
def crear_vehiculo(db):
    def _crear(cliente: Cliente, placa: str = "ABC123", **campos) -> Vehiculo:
        vehiculo = Vehiculo(
            taller_id=cliente.taller_id,
            cliente_id=cliente.id,
            placa=placa,
            marca=campos.pop("marca", "Mazda"),
            modelo=campos.pop("modelo", "3"),
            **campos,
        )
        db.add(vehiculo)
        db.commit()
        return vehiculo

    return _crear


def iniciar_sesion(cliente: TestClient, email: str, clave: str = CLAVE):
    return cliente.post("/api/v1/auth/login", json={"email": email, "password": clave})
