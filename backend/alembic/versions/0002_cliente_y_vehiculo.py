"""Tablas cliente y vehiculo (docs/modelo-datos.md §3.3 y §3.4)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cliente",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=False),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("documento", sa.String(20), nullable=True),
        sa.Column("autoriza_datos", sa.Boolean(), nullable=False),
        sa.Column("fecha_autorizacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("anonimizado", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "autoriza_datos = true", name=op.f("ck_cliente_autoriza_datos_obligatoria")
        ),
        sa.ForeignKeyConstraint(
            ["taller_id"],
            ["taller.id"],
            name=op.f("fk_cliente_taller_id_taller"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cliente")),
    )
    op.create_index(op.f("ix_cliente_taller_id"), "cliente", ["taller_id"])
    op.create_index(
        "uq_cliente_taller_documento",
        "cliente",
        ["taller_id", "documento"],
        unique=True,
        postgresql_where=sa.text("documento IS NOT NULL"),
    )

    op.create_table(
        "vehiculo",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("cliente_id", sa.BigInteger(), nullable=False),
        sa.Column("placa", sa.String(10), nullable=False),
        sa.Column("marca", sa.String(50), nullable=False),
        sa.Column("modelo", sa.String(50), nullable=False),
        sa.Column("anio", sa.SmallInteger(), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("anio BETWEEN 1950 AND 2100", name=op.f("ck_vehiculo_anio_valido")),
        sa.ForeignKeyConstraint(
            ["taller_id"],
            ["taller.id"],
            name=op.f("fk_vehiculo_taller_id_taller"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["cliente.id"],
            name=op.f("fk_vehiculo_cliente_id_cliente"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehiculo")),
        sa.UniqueConstraint("taller_id", "placa", name="uq_vehiculo_taller_placa"),
    )
    op.create_index(op.f("ix_vehiculo_taller_id"), "vehiculo", ["taller_id"])
    op.create_index(op.f("ix_vehiculo_cliente_id"), "vehiculo", ["cliente_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_vehiculo_cliente_id"), table_name="vehiculo")
    op.drop_index(op.f("ix_vehiculo_taller_id"), table_name="vehiculo")
    op.drop_table("vehiculo")
    op.drop_index("uq_cliente_taller_documento", table_name="cliente")
    op.drop_index(op.f("ix_cliente_taller_id"), table_name="cliente")
    op.drop_table("cliente")
