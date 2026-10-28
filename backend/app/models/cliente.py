from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import false, true

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.vehiculo import Vehiculo

# Debe coincidir con la migración 0005: anonimizar borra correo y documento, desactiva al
# cliente y deja la auditoría (quién y cuándo).
ANONIMIZACION_COHERENTE = (
    "(NOT anonimizado AND anonimizado_en IS NULL AND anonimizado_por IS NULL)"
    " OR (anonimizado AND anonimizado_en IS NOT NULL AND anonimizado_por IS NOT NULL"
    " AND email IS NULL AND documento IS NULL AND NOT activo)"
)


class Cliente(Base):
    __tablename__ = "cliente"
    __table_args__ = (
        # Ley 1581: la base de datos tampoco acepta un cliente sin autorización (RN-10).
        CheckConstraint("autoriza_datos = true", name="autoriza_datos_obligatoria"),
        CheckConstraint(ANONIMIZACION_COHERENTE, name="anonimizacion_coherente"),
        # Los talleres informales a veces no piden documento, por eso la unicidad es parcial.
        Index(
            "uq_cliente_taller_documento",
            "taller_id",
            "documento",
            unique=True,
            postgresql_where=text("documento IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(120))
    telefono: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(254))
    documento: Mapped[str | None] = mapped_column(String(20))
    autoriza_datos: Mapped[bool]
    fecha_autorizacion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    anonimizado: Mapped[bool] = mapped_column(default=False, server_default=false())
    anonimizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    anonimizado_por: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vehiculos: Mapped[list["Vehiculo"]] = relationship(
        back_populates="cliente", order_by="Vehiculo.placa"
    )
    anonimizador: Mapped["Usuario | None"] = relationship(foreign_keys=[anonimizado_por])
