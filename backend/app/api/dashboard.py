from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DB, AdminORecepcion
from app.models import EstadoOrden
from app.schemas.inventario import RepuestoResumen
from app.services import dashboard as servicio

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardSalida(BaseModel):
    ordenes_por_estado: dict[EstadoOrden, int]
    entregadas_hoy: int
    stock_bajo_total: int
    stock_bajo: list[RepuestoResumen]


@router.get("", response_model=DashboardSalida)
def ver_dashboard(actual: AdminORecepcion, db: DB) -> DashboardSalida:
    """Dashboard mínimo (RF-14). El mecánico tiene su vista "Mis órdenes" (SPEC §3)."""
    return DashboardSalida.model_validate(servicio.resumen(db, actual), from_attributes=True)
