from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DB, SoloAdmin, UsuarioActual
from app.schemas.comunes import Pagina, Paginacion
from app.schemas.inventario import (
    MovimientoCrear,
    MovimientoSalida,
    RepuestoActualizar,
    RepuestoCrear,
    RepuestoResumen,
    RepuestoSalida,
)
from app.services import inventario as servicio

router = APIRouter(prefix="/repuestos", tags=["inventario"])


@router.get("", response_model=Pagina[RepuestoResumen])
def listar_repuestos(
    actual: UsuarioActual,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    buscar: Annotated[str | None, Query(max_length=60, description="Código o nombre")] = None,
    stock_bajo: Annotated[
        bool | None, Query(description="true: solo los que están en el mínimo o por debajo")
    ] = None,
    activo: bool | None = None,
) -> Pagina[RepuestoResumen]:
    """Todos los roles consultan el inventario (SPEC §3); solo el ADMIN lo modifica."""
    repuestos, total = servicio.listar(db, actual, page, page_size, buscar, stock_bajo, activo)
    return Pagina[RepuestoResumen](
        data=[RepuestoResumen.model_validate(r) for r in repuestos],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post("", response_model=RepuestoSalida, status_code=status.HTTP_201_CREATED)
def crear_repuesto(datos: RepuestoCrear, actual: SoloAdmin, db: DB) -> RepuestoSalida:
    return RepuestoSalida.model_validate(servicio.crear(db, actual, datos))


@router.get("/{repuesto_id}", response_model=RepuestoSalida)
def obtener_repuesto(repuesto_id: int, actual: UsuarioActual, db: DB) -> RepuestoSalida:
    return RepuestoSalida.model_validate(servicio.obtener(db, actual, repuesto_id))


@router.patch("/{repuesto_id}", response_model=RepuestoSalida)
def actualizar_repuesto(
    repuesto_id: int, datos: RepuestoActualizar, actual: SoloAdmin, db: DB
) -> RepuestoSalida:
    """El stock no se edita aquí: solo cambia con entradas, ajustes y órdenes."""
    return RepuestoSalida.model_validate(servicio.actualizar(db, actual, repuesto_id, datos))


@router.get("/{repuesto_id}/movimientos", response_model=Pagina[MovimientoSalida])
def listar_movimientos(
    repuesto_id: int,
    actual: SoloAdmin,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Pagina[MovimientoSalida]:
    movimientos, total = servicio.listar_movimientos(db, actual, repuesto_id, page, page_size)
    return Pagina[MovimientoSalida](
        data=[MovimientoSalida.model_validate(m) for m in movimientos],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post(
    "/{repuesto_id}/movimientos",
    response_model=RepuestoSalida,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimiento(
    repuesto_id: int, datos: MovimientoCrear, actual: SoloAdmin, db: DB
) -> RepuestoSalida:
    """Entrada de mercancía o ajuste por conteo físico; cada uno queda como movimiento."""
    return RepuestoSalida.model_validate(
        servicio.registrar_movimiento(db, actual, repuesto_id, datos)
    )
