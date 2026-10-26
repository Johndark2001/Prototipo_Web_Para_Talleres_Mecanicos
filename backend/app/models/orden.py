import enum
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.cliente import Cliente
from app.models.inventario import CANTIDAD, DINERO, Repuesto, Servicio
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo


class EstadoOrden(enum.StrEnum):
    RECIBIDO = "RECIBIDO"
    EN_DIAGNOSTICO = "EN_DIAGNOSTICO"
    ESPERANDO_REPUESTOS = "ESPERANDO_REPUESTOS"
    REPARADO = "REPARADO"
    ENTREGADO = "ENTREGADO"
    CANCELADA = "CANCELADA"


ESTADOS_FINALES = frozenset({EstadoOrden.ENTREGADO, EstadoOrden.CANCELADA})
TIPO_ESTADO_ORDEN = Enum(EstadoOrden, name="estado_orden")
CENTAVO = Decimal("0.01")


def subtotal_linea(cantidad: Decimal, precio_unitario: Decimal) -> Decimal:
    """Cantidad × precio, redondeado al centavo (1,5 L × $32.333 = $48.499,50)."""
    return (cantidad * precio_unitario).quantize(CENTAVO, rounding=ROUND_HALF_UP)


class OrdenTrabajo(Base):
    __tablename__ = "orden_trabajo"
    __table_args__ = (
        UniqueConstraint("taller_id", "numero", name="uq_orden_taller_numero"),
        Index("ix_orden_taller_estado", "taller_id", "estado"),
        Index("ix_orden_taller_fecha", "taller_id", "fecha_ingreso"),
        # RN-08: la base de datos también impide dos órdenes abiertas para el mismo carro.
        Index(
            "uq_orden_vehiculo_abierta",
            "vehiculo_id",
            unique=True,
            postgresql_where=text("estado NOT IN ('ENTREGADO', 'CANCELADA')"),
        ),
        CheckConstraint("kilometraje >= 0", name="kilometraje_no_negativo"),
        CheckConstraint(
            "estado <> 'CANCELADA' OR motivo_cancelacion IS NOT NULL",
            name="motivo_cancelacion_obligatorio",
        ),
        CheckConstraint(
            "estado <> 'ENTREGADO' OR fecha_entrega IS NOT NULL",
            name="fecha_entrega_obligatoria",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    taller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("taller.id", ondelete="RESTRICT"))
    numero: Mapped[int] = mapped_column(Integer)
    vehiculo_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vehiculo.id", ondelete="RESTRICT"), index=True
    )
    # Dueño en el momento de la orden: si el carro se vende, el historial no cambia.
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cliente.id", ondelete="RESTRICT"), index=True
    )
    mecanico_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT"), index=True
    )
    creado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    codigo_seguimiento: Mapped[str] = mapped_column(String(32), unique=True)
    estado: Mapped[EstadoOrden] = mapped_column(
        TIPO_ESTADO_ORDEN,
        default=EstadoOrden.RECIBIDO,
        server_default=EstadoOrden.RECIBIDO.value,
    )
    kilometraje: Mapped[int | None] = mapped_column(Integer)
    motivo_ingreso: Mapped[str] = mapped_column(Text)
    diagnostico: Mapped[str | None] = mapped_column(Text)
    trabajo_realizado: Mapped[str | None] = mapped_column(Text)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text)
    fecha_ingreso: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_entrega_estimada: Mapped[date | None] = mapped_column(Date)
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    taller: Mapped[Taller] = relationship()
    vehiculo: Mapped[Vehiculo] = relationship()
    cliente: Mapped[Cliente] = relationship()
    mecanico: Mapped[Usuario | None] = relationship(foreign_keys=[mecanico_id])
    creador: Mapped[Usuario] = relationship(foreign_keys=[creado_por])
    historial: Mapped[list["HistorialEstadoOrden"]] = relationship(
        order_by="[HistorialEstadoOrden.fecha, HistorialEstadoOrden.id]"
    )
    asignaciones: Mapped[list["AsignacionOrden"]] = relationship(
        order_by="[AsignacionOrden.fecha, AsignacionOrden.id]"
    )
    servicios: Mapped[list["OrdenServicio"]] = relationship(order_by="OrdenServicio.id")
    repuestos: Mapped[list["OrdenRepuesto"]] = relationship(order_by="OrdenRepuesto.id")

    @property
    def abierta(self) -> bool:
        return self.estado not in ESTADOS_FINALES


class HistorialEstadoOrden(Base):
    """Solo inserciones (RN-01, RN-11). Es la fuente del reporte de tiempos por etapa (R2)."""

    __tablename__ = "historial_estado_orden"
    __table_args__ = (
        Index("ix_historial_orden_fecha", "orden_id", "fecha"),
        CheckConstraint("estado_nuevo IS DISTINCT FROM estado_anterior", name="estado_distinto"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    orden_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orden_trabajo.id", ondelete="RESTRICT")
    )
    # Nulo solo en el registro de creación de la orden.
    estado_anterior: Mapped[EstadoOrden | None] = mapped_column(TIPO_ESTADO_ORDEN)
    estado_nuevo: Mapped[EstadoOrden] = mapped_column(TIPO_ESTADO_ORDEN)
    usuario_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    nota: Mapped[str | None] = mapped_column(Text)

    usuario: Mapped[Usuario] = relationship()


class AsignacionOrden(Base):
    """Solo inserciones (RN-14, P-7): cada asignación o reasignación de mecánico."""

    __tablename__ = "asignacion_orden"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    orden_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orden_trabajo.id", ondelete="RESTRICT"), index=True
    )
    mecanico_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    asignado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    nota: Mapped[str | None] = mapped_column(Text)

    mecanico: Mapped[Usuario] = relationship(foreign_keys=[mecanico_id])
    asignador: Mapped[Usuario] = relationship(foreign_keys=[asignado_por])


class OrdenServicio(Base):
    """Línea de mano de obra. Sin catálogo en el MVP: `servicio_id` queda nulo (RF-18)."""

    __tablename__ = "orden_servicio"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="precio_no_negativo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    orden_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orden_trabajo.id", ondelete="RESTRICT"), index=True
    )
    servicio_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("servicio.id", ondelete="RESTRICT")
    )
    descripcion: Mapped[str] = mapped_column(String(200))
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    precio_unitario: Mapped[Decimal] = mapped_column(DINERO)
    registrado_por: Mapped[int] = mapped_column(  # RN-15
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    servicio: Mapped[Servicio | None] = relationship()
    registrador: Mapped[Usuario] = relationship()

    @property
    def subtotal(self) -> Decimal:
        return subtotal_linea(self.cantidad, self.precio_unitario)


class OrdenRepuesto(Base):
    """Repuesto consumido. El precio es una copia del catálogo al registrarlo (RN-05)."""

    __tablename__ = "orden_repuesto"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="precio_no_negativo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    orden_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orden_trabajo.id", ondelete="RESTRICT"), index=True
    )
    repuesto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("repuesto.id", ondelete="RESTRICT"), index=True
    )
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    precio_unitario: Mapped[Decimal] = mapped_column(DINERO)
    registrado_por: Mapped[int] = mapped_column(  # RN-15
        BigInteger, ForeignKey("usuario.id", ondelete="RESTRICT")
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    repuesto: Mapped[Repuesto] = relationship()
    registrador: Mapped[Usuario] = relationship()

    @property
    def subtotal(self) -> Decimal:
        return subtotal_linea(self.cantidad, self.precio_unitario)
