from math import ceil
from typing import Annotated

from pydantic import BaseModel, StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
# Límite superior para evitar que un texto enorme consuma CPU al calcular el hash.
Clave = Annotated[str, StringConstraints(min_length=8, max_length=128)]


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
