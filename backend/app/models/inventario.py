import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import true

from app.core.db import Base
from app.models.usuario import Usuario

# Montos en pesos y cantidades con decimales exactos, nunca float (RN-19).
DINERO = Numeric(12, 2)
CANTIDAD = Numeric(10, 2)


class TipoMovimiento(enum.StrEnum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"
    DEVOLUCION = "DEVOLUCION"


class Servicio(Base):
    """Catálogo de mano de obra (RF-18, aplazado). La tabla existe porque orden_servicio la
    referencia; mientras tanto la mano de obra se escribe como texto libre (SPEC §17.1)."""

    __tablename__ = "servicio"
    __table_args__ = (
        UniqueConstraint("taller_id", "nombre", name="uq_servicio_taller_nombre"),
        CheckConstraint("precio_referencia >= 0", name="precio_no_negativo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"))
    nombre: Mapped[str] = mapped_column(String(120))
    precio_referencia: Mapped[Decimal] = mapped_column(DINERO)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class Repuesto(Base):
    __tablename__ = "repuesto"
    __table_args__ = (
        UniqueConstraint("taller_id", "codigo", name="uq_repuesto_taller_codigo"),
        CheckConstraint("precio_venta >= 0", name="precio_no_negativo"),
        # RN-02: la base de datos también impide que el stock quede negativo.
        CheckConstraint("stock_actual >= 0", name="stock_no_negativo"),
        CheckConstraint("stock_minimo >= 0", name="stock_minimo_no_negativo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"))
    codigo: Mapped[str] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(120))
    unidad: Mapped[str] = mapped_column(String(20), default="unidad", server_default="unidad")
    precio_venta: Mapped[Decimal] = mapped_column(DINERO)
    stock_actual: Mapped[Decimal] = mapped_column(
        CANTIDAD, default=Decimal(0), server_default=text("0")
    )
    stock_minimo: Mapped[Decimal] = mapped_column(
        CANTIDAD, default=Decimal(0), server_default=text("0")
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def stock_bajo(self) -> bool:
        """RN-04: alerta cuando el stock queda igual o por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo


class MovimientoInventario(Base):
    """Solo inserciones (RN-11): explica cada cambio del stock de un repuesto."""

    __tablename__ = "movimiento_inventario"
    __table_args__ = (
        Index("ix_movimiento_repuesto_fecha", "repuesto_id", "fecha"),
        CheckConstraint(
            "(tipo IN ('ENTRADA', 'DEVOLUCION') AND cantidad > 0)"
            " OR (tipo = 'SALIDA' AND cantidad < 0)"
            " OR (tipo = 'AJUSTE' AND cantidad <> 0)",
            name="signo_segun_tipo",
        ),
        CheckConstraint(
            "tipo NOT IN ('SALIDA', 'DEVOLUCION') OR orden_id IS NOT NULL",
            name="orden_obligatoria",
        ),
        CheckConstraint("stock_resultante >= 0", name="stock_resultante_no_negativo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    repuesto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("repuesto.id", ondelete="RESTRICT")
    )
    orden_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("orden_trabajo.id", ondelete="RESTRICT"), index=True
    )
    usuario_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    tipo: Mapped[TipoMovimiento] = mapped_column(Enum(TipoMovimiento, name="tipo_movimiento"))
    # Con signo: positiva si entra al stock, negativa si sale.
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    stock_resultante: Mapped[Decimal] = mapped_column(CANTIDAD)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    nota: Mapped[str | None] = mapped_column(Text)

    usuario: Mapped[Usuario] = relationship()
    orden: Mapped["OrdenTrabajo | None"] = relationship()  # noqa: F821
