import re
from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from app.models.vehiculo import TipoVehiculo
from app.schemas.comunes import error_campo, rechazar_nulo, texto_opcional, vacio_a_nulo

# Las placas colombianas tienen 5 (motos antiguas) o 6 caracteres; 7 deja margen.
PATRON_PLACA = re.compile(r"[A-Z0-9]{5,7}")


def normalizar_placa(valor: str) -> str:
    """RN-20: mayúsculas, sin espacios ni guiones. "abc-123 " y "ABC 123" son la misma placa."""
    return re.sub(r"[\s-]", "", valor).upper()


def _validar_placa(valor: Any) -> str:
    if not isinstance(valor, str):
        raise error_campo("Escriba la placa")
    placa = normalizar_placa(valor)
    if not PATRON_PLACA.fullmatch(placa):
        raise error_campo("La placa debe tener entre 5 y 7 letras o números, por ejemplo ABC123")
    return placa


Placa = Annotated[str, BeforeValidator(_validar_placa)]
TextoVehiculo = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
]
# El rango va solo sobre el número: aplicado a "int | None" fallaba con el año vacío.
Anio = Annotated[Annotated[int, Field(ge=1950, le=2100)] | None, BeforeValidator(vacio_a_nulo)]
Color = texto_opcional(30)


class VehiculoCrear(BaseModel):
    placa: Placa
    # Opcional para no romper a quien ya registra sin tipo: por defecto es un carro.
    tipo: TipoVehiculo = TipoVehiculo.CARRO
    marca: TextoVehiculo
    modelo: TextoVehiculo
    anio: Anio = None
    color: Color = None
    cliente_id: int


class VehiculoActualizar(BaseModel):
    """Actualización parcial. Cambiar `cliente_id` es registrar un nuevo dueño (venta del carro)."""

    placa: Placa | None = None
    tipo: TipoVehiculo | None = None
    marca: TextoVehiculo | None = None
    modelo: TextoVehiculo | None = None
    anio: Anio = None
    color: Color = None
    cliente_id: int | None = None
    activo: bool | None = None

    _obligatorios = field_validator(
        "placa", "tipo", "marca", "modelo", "cliente_id", "activo", mode="before"
    )(rechazar_nulo)


class Propietario(BaseModel):
    """Datos del dueño que se muestran junto al carro."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    telefono: str
    activo: bool


class VehiculoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    tipo: TipoVehiculo
    marca: str
    modelo: str
    anio: int | None
    color: str | None
    activo: bool


class VehiculoSalida(VehiculoResumen):
    creado_en: datetime
    cliente: Propietario
