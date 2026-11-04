from fastapi import APIRouter

from app.api.deps import UsuarioActual
from app.models import TipoVehiculo
from app.services.categorias import CATEGORIAS

router = APIRouter(prefix="/catalogos", tags=["catálogos"])


@router.get("/categorias-problema", response_model=dict[TipoVehiculo, list[str]])
def categorias_problema(_: UsuarioActual) -> dict[TipoVehiculo, list[str]]:
    """Categorías del problema por tipo de vehículo (cambio #5). "Otro" va siempre al final."""
    return {tipo: list(lista) for tipo, lista in CATEGORIAS.items()}
