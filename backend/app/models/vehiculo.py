from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import true

from app.core.db import Base
from app.models.cliente import Cliente


class Vehiculo(Base):
    __tablename__ = "vehiculo"
    __table_args__ = (
        UniqueConstraint("taller_id", "placa", name="uq_vehiculo_taller_placa"),
        CheckConstraint("anio BETWEEN 1950 AND 2100", name="anio_valido"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"), index=True
    )
    # Dueño actual. Las órdenes guardan su propio cliente para no reescribir el historial.
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cliente.id", ondelete="RESTRICT"), index=True
    )
    # Normalizada en mayúsculas, sin espacios ni guiones (RN-20).
    placa: Mapped[str] = mapped_column(String(10))
    marca: Mapped[str] = mapped_column(String(50))
    modelo: Mapped[str] = mapped_column(String(50))
    anio: Mapped[int | None] = mapped_column(SmallInteger)
    color: Mapped[str | None] = mapped_column(String(30))
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cliente: Mapped[Cliente] = relationship(back_populates="vehiculos")
