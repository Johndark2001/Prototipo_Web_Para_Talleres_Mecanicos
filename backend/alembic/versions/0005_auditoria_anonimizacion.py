"""Auditoría de la anonimización del cliente: anonimizado_en y anonimizado_por (RN-11, RNF-06)

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Un cliente anonimizado no conserva correo ni documento, queda inactivo y dice quién y
# cuándo lo anonimizó; uno sin anonimizar no tiene datos de auditoría.
ANONIMIZACION_COHERENTE = (
    "(NOT anonimizado AND anonimizado_en IS NULL AND anonimizado_por IS NULL)"
    " OR (anonimizado AND anonimizado_en IS NOT NULL AND anonimizado_por IS NOT NULL"
    " AND email IS NULL AND documento IS NULL AND NOT activo)"
)


def upgrade() -> None:
    op.add_column("cliente", sa.Column("anonimizado_en", sa.DateTime(timezone=True)))
    op.add_column("cliente", sa.Column("anonimizado_por", sa.BigInteger()))
    op.create_foreign_key(
        op.f("fk_cliente_anonimizado_por_usuario"),
        "cliente",
        "usuario",
        ["anonimizado_por"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        op.f("ck_cliente_anonimizacion_coherente"), "cliente", ANONIMIZACION_COHERENTE
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_cliente_anonimizacion_coherente"), "cliente", type_="check")
    op.drop_constraint(op.f("fk_cliente_anonimizado_por_usuario"), "cliente", type_="foreignkey")
    op.drop_column("cliente", "anonimizado_por")
    op.drop_column("cliente", "anonimizado_en")
