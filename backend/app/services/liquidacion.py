"""Liquidación de la orden (RF-12). RN-06: se calcula siempre a partir de las líneas, con el
precio copiado en cada una; no se guarda un total aparte ni se acepta uno enviado por el
cliente. Sin IVA (P-9)."""

from decimal import Decimal

from app.models import OrdenTrabajo

CERO = Decimal("0.00")


def calcular(orden: OrdenTrabajo) -> dict[str, Decimal]:
    mano_de_obra = sum((linea.subtotal for linea in orden.servicios), CERO)
    repuestos = sum((linea.subtotal for linea in orden.repuestos), CERO)
    return {"mano_de_obra": mano_de_obra, "repuestos": repuestos, "total": mano_de_obra + repuestos}
