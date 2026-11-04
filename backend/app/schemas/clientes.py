import re
from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    field_validator,
)

from app.schemas.comunes import Nombre, error_campo, rechazar_nulo, vacio_a_nulo
from app.schemas.ordenes import UsuarioResumen
from app.schemas.vehiculos import VehiculoDatos, VehiculoResumen

# La API exige la palabra escrita, no solo un "sí": anonimizar no se puede deshacer.
PALABRA_CONFIRMACION = "ANONIMIZAR"


def _validar_telefono(valor: Any) -> str:
    # Se guarda sin separadores para poder buscar "3001234567" aunque se escriba "300 123 4567".
    if not isinstance(valor, str):
        raise error_campo("Escriba el teléfono")
    telefono = re.sub(r"[\s\-.()]", "", valor)
    if not re.fullmatch(r"\+?\d{7,15}", telefono):
        raise error_campo("Escriba un teléfono de 7 a 15 dígitos")
    return telefono


def _validar_documento(valor: Any) -> Any:
    if not isinstance(valor, str):
        return valor
    documento = re.sub(r"[\s\-.]", "", valor).upper()
    if not re.fullmatch(r"[A-Z0-9]{4,20}", documento):
        raise error_campo("El documento debe tener de 4 a 20 letras o números")
    return documento


def _exigir_autorizacion(valor: bool) -> bool:
    if not valor:
        raise error_campo(
            "Sin la autorización de tratamiento de datos (Ley 1581) "
            "no se puede registrar al cliente"
        )
    return valor


def _exigir_confirmacion(valor: Any) -> str:
    if not isinstance(valor, str) or valor.strip().upper() != PALABRA_CONFIRMACION:
        raise error_campo(f"Escriba {PALABRA_CONFIRMACION} para confirmar")
    return PALABRA_CONFIRMACION


Telefono = Annotated[str, BeforeValidator(_validar_telefono)]
Correo = Annotated[
    EmailStr | None,
    BeforeValidator(vacio_a_nulo),
    AfterValidator(lambda v: v.lower() if v else v),
]
Documento = Annotated[
    str | None, BeforeValidator(_validar_documento), BeforeValidator(vacio_a_nulo)
]


class ClienteCrear(BaseModel):
    nombre: Nombre
    telefono: Telefono
    email: Correo = None
    documento: Documento = None
    # RN-10: se exige en cada alta; la fecha la pone el servidor, no el navegador.
    autoriza_datos: Annotated[bool, AfterValidator(_exigir_autorizacion)]
    # Cambio #6: el primer vehículo se registra en la misma operación. Si algo falla
    # (p. ej. la placa ya existe), no queda guardado ni el cliente ni el vehículo.
    vehiculo: VehiculoDatos | None = None


class ClienteActualizar(BaseModel):
    """Actualización parcial. La autorización no se edita: retirarla es anonimizar (RN-11)."""

    nombre: Nombre | None = None
    telefono: Telefono | None = None
    email: Correo = None
    documento: Documento = None
    activo: bool | None = None

    _obligatorios = field_validator("nombre", "telefono", "activo", mode="before")(rechazar_nulo)


class ClienteAnonimizar(BaseModel):
    """Confirmación explícita de la anonimización (RN-11)."""

    confirmacion: Annotated[str, BeforeValidator(_exigir_confirmacion)]


class ClienteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    telefono: str
    email: str | None
    documento: str | None
    autoriza_datos: bool
    fecha_autorizacion: datetime
    activo: bool
    anonimizado: bool
    anonimizado_en: datetime | None
    creado_en: datetime
    actualizado_en: datetime


class ClienteListado(ClienteSalida):
    total_vehiculos: int


class ClienteDetalle(ClienteSalida):
    vehiculos: list[VehiculoResumen]
    anonimizador: UsuarioResumen | None
