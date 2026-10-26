from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, StringConstraints, field_validator

from app.models import TipoMovimiento
from app.schemas.comunes import (
    Cantidad,
    Existencia,
    Precio,
    rechazar_nulo,
    texto_opcional,
)
from app.schemas.ordenes import UsuarioResumen


def _normalizar_codigo(valor: Any) -> Any:
    # "w712 " y "W712" son el mismo repuesto: el código se compara sin distinguir mayúsculas.
    return valor.strip().upper() if isinstance(valor, str) else valor


Codigo = Annotated[
    str,
    BeforeValidator(_normalizar_codigo),
    StringConstraints(min_length=1, max_length=30, pattern=r"^[A-Z0-9][A-Z0-9 ._/-]*$"),
]
NombreRepuesto = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)
]
Unidad = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Nota = texto_opcional(1000)


class RepuestoCrear(BaseModel):
    codigo: Codigo
    nombre: NombreRepuesto
    unidad: Unidad = "unidad"
    precio_venta: Precio
    stock_minimo: Existencia = Decimal(0)
    # El stock inicial entra como un movimiento ENTRADA: así el stock siempre se explica.
    stock_inicial: Existencia = Decimal(0)


class RepuestoActualizar(BaseModel):
    """El stock no se edita aquí: solo cambia con entradas, ajustes y órdenes (trazabilidad)."""

    codigo: Codigo | None = None
    nombre: NombreRepuesto | None = None
    unidad: Unidad | None = None
    precio_venta: Precio | None = None
    stock_minimo: Existencia | None = None
    activo: bool | None = None

    _obligatorios = field_validator(
        "codigo", "nombre", "unidad", "precio_venta", "stock_minimo", "activo", mode="before"
    )(rechazar_nulo)


class MovimientoCrear(BaseModel):
    """Entrada de mercancía (suma `cantidad`) o ajuste por conteo físico (`stock_contado`).

    Qué campo exige cada tipo lo verifica el servicio, que responde con el campo exacto.
    """

    tipo: Literal[TipoMovimiento.ENTRADA, TipoMovimiento.AJUSTE]
    cantidad: Cantidad | None = None
    stock_contado: Existencia | None = None
    nota: Nota = None


class RepuestoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    unidad: str
    precio_venta: Decimal
    stock_actual: Decimal
    stock_minimo: Decimal
    stock_bajo: bool
    activo: bool


class RepuestoSalida(RepuestoResumen):
    creado_en: datetime
    actualizado_en: datetime


class OrdenReferencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int


class MovimientoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoMovimiento
    cantidad: Decimal
    stock_resultante: Decimal
    fecha: datetime
    nota: str | None
    usuario: UsuarioResumen
    orden: OrdenReferencia | None
