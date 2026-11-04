from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import DB, AdminORecepcion, UsuarioActual
from app.models import EstadoOrden, OrdenTrabajo, Usuario
from app.schemas.comunes import Pagina, Paginacion
from app.schemas.ordenes import (
    AsignacionCrear,
    CambioEstado,
    LineaRepuestoCrear,
    LineaServicioCrear,
    OrdenActualizar,
    OrdenCrear,
    OrdenDetalle,
    OrdenResumen,
)
from app.services import informe_pdf, lineas_orden, liquidacion
from app.services import ordenes as servicio

router = APIRouter(prefix="/ordenes", tags=["ordenes"])


def _detalle(actual: Usuario, orden: OrdenTrabajo) -> OrdenDetalle:
    datos = {
        campo: getattr(orden, campo) for campo in OrdenDetalle.model_fields if hasattr(orden, campo)
    }
    return OrdenDetalle.model_validate(
        {**datos, "liquidacion": liquidacion.calcular(orden), **servicio.permisos(actual, orden)}
    )


@router.get("", response_model=Pagina[OrdenResumen])
def listar_ordenes(
    actual: UsuarioActual,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    estado: EstadoOrden | None = None,
    abiertas: Annotated[
        bool | None, Query(description="true: sin entregar ni cancelar; false: finalizadas")
    ] = None,
    mecanico_id: int | None = None,
    vehiculo_id: int | None = None,
) -> Pagina[OrdenResumen]:
    """El mecánico solo recibe las órdenes asignadas a él ("Mis órdenes")."""
    ordenes, total = servicio.listar(
        db, actual, page, page_size, estado, abiertas, mecanico_id, vehiculo_id
    )
    return Pagina[OrdenResumen](
        data=[OrdenResumen.model_validate(o) for o in ordenes],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post("", response_model=OrdenDetalle, status_code=status.HTTP_201_CREATED)
def crear_orden(datos: OrdenCrear, actual: AdminORecepcion, db: DB) -> OrdenDetalle:
    return _detalle(actual, servicio.crear(db, actual, datos))


@router.get("/{orden_id}", response_model=OrdenDetalle)
def obtener_orden(orden_id: int, actual: UsuarioActual, db: DB) -> OrdenDetalle:
    return _detalle(actual, servicio.obtener(db, actual, orden_id))


@router.get(
    "/{orden_id}/informe.pdf",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def descargar_informe(orden_id: int, actual: UsuarioActual, db: DB) -> Response:
    """Informe final para el cliente; solo si la orden fue ENTREGADA (409 en otro caso)."""
    orden = servicio.obtener(db, actual, orden_id)
    return respuesta_pdf(informe_pdf.generar(orden), informe_pdf.nombre_archivo(orden))


def respuesta_pdf(contenido: bytes, archivo: str) -> Response:
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{archivo}"',
            "Cache-Control": "no-store",
        },
    )


@router.patch("/{orden_id}", response_model=OrdenDetalle)
def actualizar_orden(
    orden_id: int, datos: OrdenActualizar, actual: UsuarioActual, db: DB
) -> OrdenDetalle:
    """Diagnóstico y trabajo realizado (también el mecánico asignado) y datos de recepción."""
    return _detalle(actual, servicio.actualizar(db, actual, orden_id, datos))


@router.post(
    "/{orden_id}/historial", response_model=OrdenDetalle, status_code=status.HTTP_201_CREATED
)
def cambiar_estado(
    orden_id: int, datos: CambioEstado, actual: UsuarioActual, db: DB
) -> OrdenDetalle:
    """Cambia el estado: cada cambio es un registro nuevo del historial (RN-01, SPEC §7)."""
    return _detalle(actual, servicio.cambiar_estado(db, actual, orden_id, datos))


@router.post(
    "/{orden_id}/asignaciones", response_model=OrdenDetalle, status_code=status.HTTP_201_CREATED
)
def asignar_mecanico(
    orden_id: int, datos: AsignacionCrear, actual: AdminORecepcion, db: DB
) -> OrdenDetalle:
    """Asigna o reasigna el mecánico; cada cambio queda registrado (RN-14)."""
    return _detalle(actual, servicio.asignar(db, actual, orden_id, datos))


@router.post(
    "/{orden_id}/servicios", response_model=OrdenDetalle, status_code=status.HTTP_201_CREATED
)
def agregar_servicio(
    orden_id: int, datos: LineaServicioCrear, actual: UsuarioActual, db: DB
) -> OrdenDetalle:
    """Mano de obra en texto libre (RF-12)."""
    return _detalle(actual, lineas_orden.agregar_servicio(db, actual, orden_id, datos))


@router.delete("/{orden_id}/servicios/{linea_id}", response_model=OrdenDetalle)
def quitar_servicio(orden_id: int, linea_id: int, actual: UsuarioActual, db: DB) -> OrdenDetalle:
    return _detalle(actual, lineas_orden.quitar_servicio(db, actual, orden_id, linea_id))


@router.post(
    "/{orden_id}/repuestos", response_model=OrdenDetalle, status_code=status.HTTP_201_CREATED
)
def agregar_repuesto(
    orden_id: int, datos: LineaRepuestoCrear, actual: UsuarioActual, db: DB
) -> OrdenDetalle:
    """Descuenta el stock en la misma operación; si no alcanza responde 409 (RF-09, RN-02)."""
    return _detalle(actual, lineas_orden.agregar_repuesto(db, actual, orden_id, datos))


@router.delete("/{orden_id}/repuestos/{linea_id}", response_model=OrdenDetalle)
def quitar_repuesto(orden_id: int, linea_id: int, actual: UsuarioActual, db: DB) -> OrdenDetalle:
    """El repuesto vuelve al stock con un movimiento DEVOLUCION (RN-03)."""
    return _detalle(actual, lineas_orden.quitar_repuesto(db, actual, orden_id, linea_id))
