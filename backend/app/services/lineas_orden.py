"""Mano de obra y repuestos de la orden (RF-09, RF-12; S3-7).

Pueden registrarlos quienes pueden escribir el trabajo de la orden: ADMIN, RECEPCION y el
mecánico asignado (SPEC §3). La orden se bloquea primero y el repuesto después; cancelar
una orden sigue el mismo orden, así que las dos operaciones no se bloquean mutuamente.
"""

from sqlalchemy.orm import Session

from app.core.errores import NoEncontrado, SinPermiso
from app.models import OrdenRepuesto, OrdenServicio, OrdenTrabajo, Usuario
from app.schemas.ordenes import LineaRepuestoCrear, LineaServicioCrear
from app.services import inventario as servicio_inventario
from app.services import ordenes as servicio_ordenes


def _orden_editable(db: Session, actual: Usuario, orden_id: int) -> OrdenTrabajo:
    orden = servicio_ordenes.obtener_bloqueada(db, actual, orden_id)
    servicio_ordenes.exigir_abierta(orden)  # RN-07
    if not servicio_ordenes.permisos(actual, orden)["puede_editar_trabajo"]:
        raise SinPermiso(
            "Solo el mecánico asignado, recepción o el administrador registran el trabajo"
        )
    return orden


def _linea(lineas: list, linea_id: int):
    linea = next((linea for linea in lineas if linea.id == linea_id), None)
    if linea is None:
        raise NoEncontrado("Esa línea no existe en la orden")
    return linea


def agregar_servicio(
    db: Session, actual: Usuario, orden_id: int, datos: LineaServicioCrear
) -> OrdenTrabajo:
    orden = _orden_editable(db, actual, orden_id)
    orden.servicios.append(
        OrdenServicio(
            descripcion=datos.descripcion,
            cantidad=datos.cantidad,
            precio_unitario=datos.precio_unitario,
            registrado_por=actual.id,
        )
    )
    db.commit()
    return servicio_ordenes.obtener(db, actual, orden.id)


def quitar_servicio(db: Session, actual: Usuario, orden_id: int, linea_id: int) -> OrdenTrabajo:
    orden = _orden_editable(db, actual, orden_id)
    db.delete(_linea(orden.servicios, linea_id))
    db.commit()
    return servicio_ordenes.obtener(db, actual, orden.id)


def agregar_repuesto(
    db: Session, actual: Usuario, orden_id: int, datos: LineaRepuestoCrear
) -> OrdenTrabajo:
    orden = _orden_editable(db, actual, orden_id)
    # RN-02: descuenta el stock en la misma transacción; si no alcanza, nada se guarda.
    repuesto = servicio_inventario.descontar_para_orden(
        db, actual, datos.repuesto_id, datos.cantidad, orden
    )
    orden.repuestos.append(
        OrdenRepuesto(
            repuesto_id=repuesto.id,
            cantidad=datos.cantidad,
            precio_unitario=repuesto.precio_venta,  # RN-05
            registrado_por=actual.id,
        )
    )
    db.commit()
    return servicio_ordenes.obtener(db, actual, orden.id)


def quitar_repuesto(db: Session, actual: Usuario, orden_id: int, linea_id: int) -> OrdenTrabajo:
    orden = _orden_editable(db, actual, orden_id)
    linea = _linea(orden.repuestos, linea_id)
    servicio_inventario.devolver_a_stock(  # RN-03
        db,
        actual,
        linea.repuesto_id,
        linea.cantidad,
        orden,
        nota=f"Se quitó de la orden #{orden.numero}",
    )
    db.delete(linea)
    db.commit()
    return servicio_ordenes.obtener(db, actual, orden.id)
