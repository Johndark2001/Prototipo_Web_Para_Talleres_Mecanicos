"""Tablas orden_trabajo, historial_estado_orden y asignacion_orden (docs/modelo-datos.md §3.5–§3.7)

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Lo usan tres columnas: se crea una sola vez y no al crear cada tabla.
ESTADO_ORDEN = postgresql.ENUM(
    "RECIBIDO",
    "EN_DIAGNOSTICO",
    "ESPERANDO_REPUESTOS",
    "REPARADO",
    "ENTREGADO",
    "CANCELADA",
    name="estado_orden",
    create_type=False,
)


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


def upgrade() -> None:
    ESTADO_ORDEN.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "orden_trabajo",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("vehiculo_id", sa.BigInteger(), nullable=False),
        sa.Column("cliente_id", sa.BigInteger(), nullable=False),
        sa.Column("mecanico_id", sa.BigInteger(), nullable=True),
        sa.Column("creado_por", sa.BigInteger(), nullable=False),
        sa.Column("codigo_seguimiento", sa.String(32), nullable=False),
        sa.Column("estado", ESTADO_ORDEN, server_default="RECIBIDO", nullable=False),
        sa.Column("kilometraje", sa.Integer(), nullable=True),
        sa.Column("motivo_ingreso", sa.Text(), nullable=False),
        sa.Column("diagnostico", sa.Text(), nullable=True),
        sa.Column("trabajo_realizado", sa.Text(), nullable=True),
        sa.Column("motivo_cancelacion", sa.Text(), nullable=True),
        _fecha_ahora("fecha_ingreso"),
        sa.Column("fecha_entrega_estimada", sa.Date(), nullable=True),
        sa.Column("fecha_entrega", sa.DateTime(timezone=True), nullable=True),
        _fecha_ahora("actualizado_en"),
        sa.CheckConstraint(
            "kilometraje >= 0", name=op.f("ck_orden_trabajo_kilometraje_no_negativo")
        ),
        sa.CheckConstraint(
            "estado <> 'CANCELADA' OR motivo_cancelacion IS NOT NULL",
            name=op.f("ck_orden_trabajo_motivo_cancelacion_obligatorio"),
        ),
        sa.CheckConstraint(
            "estado <> 'ENTREGADO' OR fecha_entrega IS NOT NULL",
            name=op.f("ck_orden_trabajo_fecha_entrega_obligatoria"),
        ),
        _fk("orden_trabajo", "taller_id", "taller.id"),
        _fk("orden_trabajo", "vehiculo_id", "vehiculo.id"),
        _fk("orden_trabajo", "cliente_id", "cliente.id"),
        _fk("orden_trabajo", "mecanico_id", "usuario.id"),
        _fk("orden_trabajo", "creado_por", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orden_trabajo")),
        sa.UniqueConstraint("taller_id", "numero", name="uq_orden_taller_numero"),
        sa.UniqueConstraint("codigo_seguimiento", name=op.f("uq_orden_trabajo_codigo_seguimiento")),
    )
    op.create_index("ix_orden_taller_estado", "orden_trabajo", ["taller_id", "estado"])
    op.create_index("ix_orden_taller_fecha", "orden_trabajo", ["taller_id", "fecha_ingreso"])
    op.create_index(op.f("ix_orden_trabajo_vehiculo_id"), "orden_trabajo", ["vehiculo_id"])
    op.create_index(op.f("ix_orden_trabajo_cliente_id"), "orden_trabajo", ["cliente_id"])
    op.create_index(op.f("ix_orden_trabajo_mecanico_id"), "orden_trabajo", ["mecanico_id"])
    # RN-08: como máximo una orden abierta por vehículo.
    op.create_index(
        "uq_orden_vehiculo_abierta",
        "orden_trabajo",
        ["vehiculo_id"],
        unique=True,
        postgresql_where=sa.text("estado NOT IN ('ENTREGADO', 'CANCELADA')"),
    )

    op.create_table(
        "historial_estado_orden",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("orden_id", sa.BigInteger(), nullable=False),
        sa.Column("estado_anterior", ESTADO_ORDEN, nullable=True),
        sa.Column("estado_nuevo", ESTADO_ORDEN, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        _fecha_ahora("fecha"),
        sa.Column("nota", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "estado_nuevo IS DISTINCT FROM estado_anterior",
            name=op.f("ck_historial_estado_orden_estado_distinto"),
        ),
        _fk("historial_estado_orden", "orden_id", "orden_trabajo.id"),
        _fk("historial_estado_orden", "usuario_id", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_historial_estado_orden")),
    )
    op.create_index("ix_historial_orden_fecha", "historial_estado_orden", ["orden_id", "fecha"])

    op.create_table(
        "asignacion_orden",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("orden_id", sa.BigInteger(), nullable=False),
        sa.Column("mecanico_id", sa.BigInteger(), nullable=False),
        sa.Column("asignado_por", sa.BigInteger(), nullable=False),
        _fecha_ahora("fecha"),
        sa.Column("nota", sa.Text(), nullable=True),
        _fk("asignacion_orden", "orden_id", "orden_trabajo.id"),
        _fk("asignacion_orden", "mecanico_id", "usuario.id"),
        _fk("asignacion_orden", "asignado_por", "usuario.id"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_asignacion_orden")),
    )
    op.create_index(op.f("ix_asignacion_orden_orden_id"), "asignacion_orden", ["orden_id"])


def downgrade() -> None:
    op.drop_table("asignacion_orden")
    op.drop_table("historial_estado_orden")
    op.drop_table("orden_trabajo")
    ESTADO_ORDEN.drop(op.get_bind(), checkfirst=True)
