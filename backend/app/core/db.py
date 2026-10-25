from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import obtener_configuracion

# Nombres de restricciones predecibles: las migraciones de Alembic y el SPEC §14 los usan.
CONVENCION_NOMBRES = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCION_NOMBRES)


# Sin límite, una base caída o "dormida" (plan gratuito) deja las solicitudes colgadas.
motor = create_engine(
    obtener_configuracion().database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def obtener_db() -> Iterator[Session]:
    with SesionLocal() as db:
        yield db


def restriccion_violada(error: IntegrityError) -> str | None:
    """Nombre de la restricción que rechazó la operación (gracias a CONVENCION_NOMBRES)."""
    diagnostico = getattr(error.orig, "diag", None)
    return getattr(diagnostico, "constraint_name", None)
