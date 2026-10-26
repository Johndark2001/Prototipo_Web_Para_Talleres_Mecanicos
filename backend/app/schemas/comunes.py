from decimal import Decimal
from math import ceil
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field, StringConstraints
from pydantic_core import PydanticCustomError

from app.core.errores import TIPO_ERROR_PROPIO

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
# Límite superior para evitar que un texto enorme consuma CPU al calcular el hash.
Clave = Annotated[str, StringConstraints(min_length=8, max_length=128)]
# Pesos colombianos y cantidades con decimales exactos (RN-19). Los límites siguen las
# columnas NUMERIC(12,2) y NUMERIC(10,2) de la base de datos.
Precio = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Cantidad = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
Existencia = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]


def error_campo(mensaje: str) -> PydanticCustomError:
    """Error de validación con mensaje propio, que la API devuelve tal cual (RNF-08)."""
    return PydanticCustomError(TIPO_ERROR_PROPIO, mensaje)


def vacio_a_nulo(valor: Any) -> Any:
    """Un campo opcional que el formulario envía en blanco se guarda como nulo."""
    if isinstance(valor, str) and not valor.strip():
        return None
    return valor


def rechazar_nulo(valor: Any) -> Any:
    """En actualizaciones parciales, un campo obligatorio puede omitirse pero no vaciarse."""
    if valor is None:
        raise error_campo("Este campo es obligatorio")
    return valor


def texto_opcional(max_length: int):
    # Las restricciones van solo sobre el texto; aplicadas a "str | None" fallan con None.
    return Annotated[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=max_length)] | None,
        BeforeValidator(vacio_a_nulo),
    ]


class Paginacion(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

    @classmethod
    def calcular(cls, page: int, page_size: int, total_items: int) -> "Paginacion":
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=max(1, ceil(total_items / page_size)),
        )


class Pagina[T](BaseModel):
    data: list[T]
    pagination: Paginacion
