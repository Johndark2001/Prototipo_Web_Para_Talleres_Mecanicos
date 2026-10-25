from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DB, AdminORecepcion
from app.services import usuarios as servicio

router = APIRouter(prefix="/mecanicos", tags=["ordenes"])


class MecanicoSalida(BaseModel):
    id: int
    nombre: str
    ordenes_abiertas: int


@router.get("", response_model=list[MecanicoSalida])
def listar_mecanicos(actual: AdminORecepcion, db: DB) -> list[MecanicoSalida]:
    """Para asignar órdenes. Recepción lo necesita y no tiene acceso a /usuarios."""
    return [
        MecanicoSalida(id=u.id, nombre=u.nombre, ordenes_abiertas=n)
        for u, n in servicio.listar_mecanicos(db, actual)
    ]
