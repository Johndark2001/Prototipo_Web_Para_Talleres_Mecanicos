"""Dashboard mínimo (RF-14, SPEC §17.1): conteos por estado y alertas de stock."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ESTADOS_FINALES, EstadoOrden, OrdenTrabajo, Repuesto, Usuario
from app.services.inventario import STOCK_BAJO

# Colombia no tiene horario de verano: UTC−5 todo el año.
HORA_COLOMBIA = timezone(timedelta(hours=-5), "COT")
MAXIMO_ALERTAS = 5


def resumen(db: Session, actual: Usuario) -> dict:
    del_taller = OrdenTrabajo.taller_id == actual.taller_id
    por_estado = dict(
        db.execute(
            select(OrdenTrabajo.estado, func.count())
            .where(del_taller, OrdenTrabajo.estado.notin_(ESTADOS_FINALES))
            .group_by(OrdenTrabajo.estado)
        ).all()
    )
    abiertos = [e for e in EstadoOrden if e not in ESTADOS_FINALES]

    inicio_del_dia = datetime.now(HORA_COLOMBIA).replace(hour=0, minute=0, second=0, microsecond=0)
    entregadas_hoy = db.scalar(
        select(func.count())
        .select_from(OrdenTrabajo)
        .where(
            del_taller,
            OrdenTrabajo.estado == EstadoOrden.ENTREGADO,
            OrdenTrabajo.fecha_entrega >= inicio_del_dia,
        )
    )

    con_alerta = [Repuesto.taller_id == actual.taller_id, Repuesto.activo, STOCK_BAJO]
    total_alertas = db.scalar(select(func.count()).select_from(Repuesto).where(*con_alerta))
    # Primero los más urgentes: los que más lejos están de su mínimo (o agotados).
    alertas = db.scalars(
        select(Repuesto)
        .where(*con_alerta)
        .order_by(Repuesto.stock_actual - Repuesto.stock_minimo, Repuesto.nombre)
        .limit(MAXIMO_ALERTAS)
    ).all()

    return {
        "ordenes_por_estado": {estado: por_estado.get(estado, 0) for estado in abiertos},
        "entregadas_hoy": entregadas_hoy or 0,
        "stock_bajo_total": total_alertas or 0,
        "stock_bajo": list(alertas),
    }
