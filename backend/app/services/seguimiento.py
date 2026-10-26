"""Seguimiento público de la orden por enlace (RF-13, ADR-005).

Muestra solo: taller, número, placa enmascarada, marca y modelo, estado con su línea de
tiempo y la liquidación. Nunca datos personales del cliente, notas internas ni usuarios.
"""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.errores import NoEncontrado
from app.models import OrdenRepuesto, OrdenTrabajo

# secrets.token_urlsafe(16): 22 caracteres de base64 para URL. Lo demás ni se consulta.
PATRON_CODIGO = re.compile(r"[A-Za-z0-9_-]{16,43}")


def enmascarar_placa(placa: str) -> str:
    """ABC123 → ABC***: reconocible para el dueño, inútil para un extraño."""
    return placa[:3] + "*" * (len(placa) - 3)


def obtener_por_codigo(db: Session, codigo: str) -> OrdenTrabajo:
    orden = None
    if PATRON_CODIGO.fullmatch(codigo):
        orden = db.scalar(
            select(OrdenTrabajo)
            .options(
                joinedload(OrdenTrabajo.taller),
                joinedload(OrdenTrabajo.vehiculo),
                selectinload(OrdenTrabajo.historial),
                selectinload(OrdenTrabajo.servicios),
                selectinload(OrdenTrabajo.repuestos).joinedload(OrdenRepuesto.repuesto),
            )
            .where(OrdenTrabajo.codigo_seguimiento == codigo)
        )
    if orden is None:
        raise NoEncontrado("No encontramos esta orden. Revise el enlace que le enviaron.")
    return orden
