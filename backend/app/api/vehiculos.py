from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DB, AdminORecepcion, UsuarioActual
from app.schemas.comunes import Pagina, Paginacion
from app.schemas.vehiculos import VehiculoActualizar, VehiculoCrear, VehiculoSalida
from app.services import vehiculos as servicio

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])


@router.get("", response_model=Pagina[VehiculoSalida])
def listar_vehiculos(
    actual: UsuarioActual,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    placa: Annotated[
        str | None, Query(max_length=20, description="Placa completa o parcial")
    ] = None,
    cliente_id: int | None = None,
    activo: bool | None = None,
) -> Pagina[VehiculoSalida]:
    vehiculos, total = servicio.listar(db, actual, page, page_size, placa, cliente_id, activo)
    return Pagina[VehiculoSalida](
        data=[VehiculoSalida.model_validate(v) for v in vehiculos],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post("", response_model=VehiculoSalida, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(datos: VehiculoCrear, actual: AdminORecepcion, db: DB) -> VehiculoSalida:
    return VehiculoSalida.model_validate(servicio.crear(db, actual, datos))


@router.get("/{vehiculo_id}", response_model=VehiculoSalida)
def obtener_vehiculo(vehiculo_id: int, actual: UsuarioActual, db: DB) -> VehiculoSalida:
    return VehiculoSalida.model_validate(servicio.obtener(db, actual, vehiculo_id))


@router.patch("/{vehiculo_id}", response_model=VehiculoSalida)
def actualizar_vehiculo(
    vehiculo_id: int, datos: VehiculoActualizar, actual: AdminORecepcion, db: DB
) -> VehiculoSalida:
    """Edita datos, cambia de dueño (`cliente_id`) o desactiva (`activo`). No se borra."""
    return VehiculoSalida.model_validate(servicio.actualizar(db, actual, vehiculo_id, datos))
