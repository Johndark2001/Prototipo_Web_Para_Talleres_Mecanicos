from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DB
from app.core.errores import ServicioNoDisponible

router = APIRouter(tags=["salud"])


@router.get("/salud")
def salud(db: DB) -> dict:
    """Comprueba que la API responde y que la base de datos está conectada."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise ServicioNoDisponible("La base de datos no responde") from exc
    return {"estado": "ok", "base_de_datos": "ok"}
