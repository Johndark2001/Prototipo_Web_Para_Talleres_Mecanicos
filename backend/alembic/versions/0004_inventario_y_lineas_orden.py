"""Inventario y líneas de la orden: servicio, repuesto, orden_servicio, orden_repuesto y
movimiento_inventario (docs/modelo-datos.md §3.8–§3.12)

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TIPO_MOVIMIENTO = postgresql.ENUM(
    "ENTRADA", "SALIDA", "AJUSTE", "DEVOLUCION", name="tipo_movimiento", create_type=False
)
DINERO = sa.Numeric(12, 2)
CANTIDAD = sa.Numeric(10, 2)


def _fk(tabla: str, columna: str, destino: str) -> sa.ForeignKeyConstraint:
    tabla_destino = destino.split(".")[0]
    return sa.ForeignKeyConstraint(
        [columna],
        [destino],
        name=op.f(f"fk_{tabla}_{columna}_{tabla_destino}"),
        ondelete="RESTRICT",
    )


def _fecha_ahora(nombre: str) -> sa.Column:
    return sa.Column(
        nombre, sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )


def _check(tabla: str, nombre: str, condicion: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(condicion, name=op.f(f"ck_{tabla}_{nombre}"))


def upgrade() -> None:
    TIPO_MOVIMIENTO.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "servicio",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("precio_referencia", DINERO, nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        _check("servicio", "precio_no_negativo", "precio_referencia >= 0"),
        _fk("servicio", "taller_id", "taller.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_servicio")),
        sa.UniqueConstraint("taller_id", "nombre", name="uq_servicio_taller_nombre"),
    )

    op.create_table(
        "repuesto",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("unidad", sa.String(20), server_default="unidad", nullable=False),
        sa.Column("precio_venta", DINERO, nullable=False),
        sa.Column("stock_actual", CANTIDAD, server_default=sa.text("0"), nullable=False),
        sa.Column("stock_minimo", CANTIDAD, server_default=sa.text("0"), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        _fecha_ahora("creado_en"),
        _fecha_ahora("actualizado_en"),
        _check("repuesto", "precio_no_negativo", "precio_venta >= 0"),
        _check("repuesto", "stock_no_negativo", "stock_actual >= 0"),
        _check("repuesto", "stock_minimo_no_negativo", "stock_minimo >= 0"),
        _fk("repuesto", "taller_id", "taller.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repuesto")),
        sa.UniqueConstraint("taller_id", "codigo", name="uq_repuesto_taller_codigo"),
    )

    op.create_table(
        "orden_servicio",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("orden_id", sa.BigInteger(), nullable=False),
        sa.Column("servicio_id", sa.BigInteger(), nullable=True),
        sa.Column("descripcion", sa.String(200), nullable=False),
        sa.Column("cantidad", CANTIDAD, nullable=False),
        sa.Column("precio_unitario", DINERO, nullable=False),
        sa.Column("registrado_por", sa.BigInteger(), nullable=False),
        _fecha_ahora("creado_en"),
        _check("orden_servicio", "cantidad_positiva", "cantidad > 0"),
        _check("orden_servicio", "precio_no_negativo", "precio_unitario >= 0"),
        _fk("orden_servicio", "orden_id", "orden_trabajo.id"),
        _fk("orden_servicio", "servicio_id", "servicio.id"),
        _fk("orden_servicio", "registrado_por", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orden_servicio")),
    )
    op.create_index(op.f("ix_orden_servicio_orden_id"), "orden_servicio", ["orden_id"])

    op.create_table(
        "orden_repuesto",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("orden_id", sa.BigInteger(), nullable=False),
        sa.Column("repuesto_id", sa.BigInteger(), nullable=False),
        sa.Column("cantidad", CANTIDAD, nullable=False),
        sa.Column("precio_unitario", DINERO, nullable=False),
        sa.Column("registrado_por", sa.BigInteger(), nullable=False),
        _fecha_ahora("creado_en"),
        _check("orden_repuesto", "cantidad_positiva", "cantidad > 0"),
        _check("orden_repuesto", "precio_no_negativo", "precio_unitario >= 0"),
        _fk("orden_repuesto", "orden_id", "orden_trabajo.id"),
        _fk("orden_repuesto", "repuesto_id", "repuesto.id"),
        _fk("orden_repuesto", "registrado_por", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orden_repuesto")),
    )
    op.create_index(op.f("ix_orden_repuesto_orden_id"), "orden_repuesto", ["orden_id"])
    op.create_index(op.f("ix_orden_repuesto_repuesto_id"), "orden_repuesto", ["repuesto_id"])

    op.create_table(
        "movimiento_inventario",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("repuesto_id", sa.BigInteger(), nullable=False),
        sa.Column("orden_id", sa.BigInteger(), nullable=True),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo", TIPO_MOVIMIENTO, nullable=False),
        sa.Column("cantidad", CANTIDAD, nullable=False),
        sa.Column("stock_resultante", CANTIDAD, nullable=False),
        _fecha_ahora("fecha"),
        sa.Column("nota", sa.Text(), nullable=True),
        _check(
            "movimiento_inventario",
            "signo_segun_tipo",
            "(tipo IN ('ENTRADA', 'DEVOLUCION') AND cantidad > 0)"
            " OR (tipo = 'SALIDA' AND cantidad < 0)"
            " OR (tipo = 'AJUSTE' AND cantidad <> 0)",
        ),
        _check(
            "movimiento_inventario",
            "orden_obligatoria",
            "tipo NOT IN ('SALIDA', 'DEVOLUCION') OR orden_id IS NOT NULL",
        ),
        _check("movimiento_inventario", "stock_resultante_no_negativo", "stock_resultante >= 0"),
        _fk("movimiento_inventario", "repuesto_id", "repuesto.id"),
        _fk("movimiento_inventario", "orden_id", "orden_trabajo.id"),
        _fk("movimiento_inventario", "usuario_id", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_movimiento_inventario")),
    )
    op.create_index(
        "ix_movimiento_repuesto_fecha", "movimiento_inventario", ["repuesto_id", "fecha"]
    )
    op.create_index(
        op.f("ix_movimiento_inventario_orden_id"), "movimiento_inventario", ["orden_id"]
    )


def downgrade() -> None:
    op.drop_table("movimiento_inventario")
    op.drop_table("orden_repuesto")
    op.drop_table("orden_servicio")
    op.drop_table("repuesto")
    op.drop_table("servicio")
    TIPO_MOVIMIENTO.drop(op.get_bind(), checkfirst=True)
