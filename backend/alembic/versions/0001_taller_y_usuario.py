"""Tablas taller y usuario (docs/modelo-datos.md §3.1 y §3.2)

Revision ID: 0001
Revises:
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROL_USUARIO = sa.Enum("ADMIN", "RECEPCION", "MECANICO", name="rol_usuario")


def upgrade() -> None:
    op.create_table(
        "taller",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("nit", sa.String(20), nullable=True),
        sa.Column("es_formal", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=True),
        sa.Column("direccion", sa.String(200), nullable=True),
        sa.Column(
            "siguiente_numero_orden", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "siguiente_numero_orden >= 1",
            name=op.f("ck_taller_siguiente_numero_orden_positivo"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_taller")),
    )

    op.create_table(
        "usuario",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("taller_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol", ROL_USUARIO, nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("ultimo_acceso", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("email = lower(email)", name=op.f("ck_usuario_email_minusculas")),
        sa.ForeignKeyConstraint(
            ["taller_id"],
            ["taller.id"],
            name=op.f("fk_usuario_taller_id_taller"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuario")),
        sa.UniqueConstraint("email", name=op.f("uq_usuario_email")),
    )
    op.create_index(op.f("ix_usuario_taller_id"), "usuario", ["taller_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_usuario_taller_id"), table_name="usuario")
    op.drop_table("usuario")
    op.drop_table("taller")
    ROL_USUARIO.drop(op.get_bind(), checkfirst=True)
