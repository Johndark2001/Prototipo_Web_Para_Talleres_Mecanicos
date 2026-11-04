"""Tipo de vehículo: carro o moto

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TIPO_VEHICULO = postgresql.ENUM("CARRO", "MOTO", name="tipo_vehiculo", create_type=False)


def upgrade() -> None:
    TIPO_VEHICULO.create(op.get_bind(), checkfirst=True)
    # Los vehículos ya registrados quedan como carros; ningún dato se pierde.
    op.add_column(
        "vehiculo",
        sa.Column("tipo", TIPO_VEHICULO, nullable=False, server_default="CARRO"),
    )


def downgrade() -> None:
    op.drop_column("vehiculo", "tipo")
    TIPO_VEHICULO.drop(op.get_bind(), checkfirst=True)
