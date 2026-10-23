from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DB, SoloAdmin
from app.models import RolUsuario
from app.schemas.comunes import Pagina, Paginacion
from app.schemas.usuarios import UsuarioActualizar, UsuarioCrear, UsuarioSalida
from app.services import usuarios as servicio

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=Pagina[UsuarioSalida])
def listar_usuarios(
    actual: SoloAdmin,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    rol: RolUsuario | None = None,
    activo: bool | None = None,
) -> Pagina[UsuarioSalida]:
    usuarios, total = servicio.listar(db, actual, page, page_size, rol, activo)
    return Pagina[UsuarioSalida](
        data=[UsuarioSalida.model_validate(u) for u in usuarios],
        pagination=Paginacion.calcular(page, page_size, total),
    )


@router.post("", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear, actual: SoloAdmin, db: DB) -> UsuarioSalida:
    return UsuarioSalida.model_validate(servicio.crear(db, actual, datos))


@router.patch("/{usuario_id}", response_model=UsuarioSalida)
def actualizar_usuario(
    usuario_id: int, datos: UsuarioActualizar, actual: SoloAdmin, db: DB
) -> UsuarioSalida:
    return UsuarioSalida.model_validate(servicio.actualizar(db, actual, usuario_id, datos))
