import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import true

from app.core.db import Base
from app.models.taller import Taller


class RolUsuario(enum.StrEnum):
    ADMIN = "ADMIN"
    RECEPCION = "RECEPCION"
    MECANICO = "MECANICO"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint("email = lower(email)", name="email_minusculas"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(120))
    # Único en todo el sistema: el login no pide elegir taller (ADR-006).
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, name="rol_usuario"))
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    taller: Mapped[Taller] = relationship()
