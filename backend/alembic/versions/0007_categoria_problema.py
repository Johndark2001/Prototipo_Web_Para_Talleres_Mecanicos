"""Categoría del problema y observación del cliente en la orden

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orden_trabajo", sa.Column("categoria_problema", sa.String(80), nullable=True))
    op.add_column("orden_trabajo", sa.Column("categoria_otro", sa.String(120), nullable=True))
    op.add_column("orden_trabajo", sa.Column("observacion_cliente", sa.Text(), nullable=True))
    op.create_check_constraint(
        "categoria_otro_solo_con_otro",
        "orden_trabajo",
        "categoria_otro IS NULL OR categoria_problema = 'Otro'",
    )
    # Las órdenes anteriores no tienen categoría: lo que se escribió como motivo de ingreso
    # pasa a ser la observación del cliente. `motivo_ingreso` no se toca.
    op.execute("UPDATE orden_trabajo SET observacion_cliente = motivo_ingreso")


def downgrade() -> None:
    op.drop_constraint("categoria_otro_solo_con_otro", "orden_trabajo", type_="check")
    op.drop_column("orden_trabajo", "observacion_cliente")
    op.drop_column("orden_trabajo", "categoria_otro")
    op.drop_column("orden_trabajo", "categoria_problema")
