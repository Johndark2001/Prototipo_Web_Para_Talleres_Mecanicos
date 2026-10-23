from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import false, true

from app.core.db import Base


class Taller(Base):
    """Tenant del sistema (ADR-006). Lo crea el desarrollador con el script de administración."""

    __tablename__ = "taller"
    __table_args__ = (
        CheckConstraint("siguiente_numero_orden >= 1", name="siguiente_numero_orden_positivo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    nit: Mapped[str | None] = mapped_column(String(20))
    es_formal: Mapped[bool] = mapped_column(default=False, server_default=false())
    telefono: Mapped[str | None] = mapped_column(String(20))
    direccion: Mapped[str | None] = mapped_column(String(200))
    siguiente_numero_orden: Mapped[int] = mapped_column(
        Integer, default=1, server_default=text("1")
    )
    activo: Mapped[bool] = mapped_column(default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
