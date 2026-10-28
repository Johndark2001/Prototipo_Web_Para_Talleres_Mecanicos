from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DB, AdminORecepcion, SoloAdmin, UsuarioActual
from app.schemas.clientes import (
    ClienteActualizar,
    ClienteAnonimizar,
    ClienteCrear,
    ClienteDetalle,
    ClienteListado,
    ClienteSalida,
)
from app.schemas.comunes import Pagina, Paginacion
from app.services import clientes as servicio

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=Pagina[ClienteListado])
def listar_clientes(
    actual: UsuarioActual,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[
        str | None, Query(max_length=120, description="Nombre, teléfono o documento")
    ] = None,
    activo: bool | None = None,
) -> Pagina[ClienteListado]:
    filas, total = servicio.listar(db, actual, page, page_size, q, activo)
    return Pagina[ClienteListado](
        data=[
            ClienteListado(**ClienteSalida.model_validate(c).model_dump(), total_vehiculos=n)
            for c, n in filas
        ],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post("", response_model=ClienteSalida, status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCrear, actual: AdminORecepcion, db: DB) -> ClienteSalida:
    return ClienteSalida.model_validate(servicio.crear(db, actual, datos))


@router.get("/{cliente_id}", response_model=ClienteDetalle)
def obtener_cliente(cliente_id: int, actual: UsuarioActual, db: DB) -> ClienteDetalle:
    return ClienteDetalle.model_validate(
        servicio.obtener(db, actual, cliente_id, con_vehiculos=True)
    )


@router.patch("/{cliente_id}", response_model=ClienteSalida)
def actualizar_cliente(
    cliente_id: int, datos: ClienteActualizar, actual: AdminORecepcion, db: DB
) -> ClienteSalida:
    """También desactiva o reactiva (`activo`): los clientes no se borran (RN-11)."""
    return ClienteSalida.model_validate(servicio.actualizar(db, actual, cliente_id, datos))


@router.post("/{cliente_id}/anonimizar", response_model=ClienteDetalle)
def anonimizar_cliente(
    cliente_id: int, datos: ClienteAnonimizar, actual: SoloAdmin, db: DB
) -> ClienteDetalle:
    """Solo el ADMIN, y escribiendo ANONIMIZAR en `confirmacion` (RN-11). No se deshace."""
    return ClienteDetalle.model_validate(servicio.anonimizar(db, actual, cliente_id))
