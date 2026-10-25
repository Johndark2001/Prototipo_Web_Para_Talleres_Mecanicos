from datetime import date, datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from app.models import EstadoOrden
from app.schemas.comunes import error_campo, rechazar_nulo, texto_opcional, vacio_a_nulo
from app.schemas.vehiculos import Propietario, VehiculoResumen
from app.services.flujo_orden import TipoTransicion

MotivoIngreso = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)
]
# Como con el año del vehículo, el rango va solo sobre el número para que el vacío sea válido.
Kilometraje = Annotated[
    Annotated[int, Field(ge=0, le=9_999_999)] | None, BeforeValidator(vacio_a_nulo)
]
TextoLargo = texto_opcional(5000)
Nota = texto_opcional(1000)


def _no_en_el_pasado(valor: date | None) -> date | None:
    if valor is not None and valor < date.today():
        raise error_campo("La fecha estimada de entrega no puede ser anterior a hoy")
    return valor


FechaEstimada = Annotated[
    date | None, BeforeValidator(vacio_a_nulo), AfterValidator(_no_en_el_pasado)
]


class OrdenCrear(BaseModel):
    """Recepción (RF-05): el carro, el motivo y, si ya se sabe, el mecánico."""

    vehiculo_id: int
    motivo_ingreso: MotivoIngreso
    kilometraje: Kilometraje = None
    fecha_entrega_estimada: FechaEstimada = None
    mecanico_id: int | None = None


class OrdenActualizar(BaseModel):
    """Actualización parcial. El mecánico asignado solo puede enviar diagnóstico y trabajo."""

    diagnostico: TextoLargo = None
    trabajo_realizado: TextoLargo = None
    motivo_ingreso: MotivoIngreso | None = None
    kilometraje: Kilometraje = None
    fecha_entrega_estimada: FechaEstimada = None

    _obligatorios = field_validator("motivo_ingreso", mode="before")(rechazar_nulo)


class CambioEstado(BaseModel):
    estado: EstadoOrden
    nota: Nota = None


class AsignacionCrear(BaseModel):
    mecanico_id: int
    nota: Nota = None


class UsuarioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class HistorialSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado_anterior: EstadoOrden | None
    estado_nuevo: EstadoOrden
    fecha: datetime
    nota: str | None
    usuario: UsuarioResumen


class AsignacionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: datetime
    nota: str | None
    mecanico: UsuarioResumen
    asignador: UsuarioResumen


class TransicionSalida(BaseModel):
    """Cambio de estado que el usuario puede pedir; la interfaz solo muestra estos (§11)."""

    estado: EstadoOrden
    tipo: TipoTransicion
    requiere_nota: bool


class OrdenResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    estado: EstadoOrden
    motivo_ingreso: str
    kilometraje: int | None
    fecha_ingreso: datetime
    fecha_entrega_estimada: date | None
    fecha_entrega: datetime | None
    actualizado_en: datetime
    vehiculo: VehiculoResumen
    cliente: Propietario
    mecanico: UsuarioResumen | None


class OrdenDetalle(OrdenResumen):
    diagnostico: str | None
    trabajo_realizado: str | None
    motivo_cancelacion: str | None
    codigo_seguimiento: str
    creador: UsuarioResumen
    historial: list[HistorialSalida]
    asignaciones: list[AsignacionSalida]
    transiciones: list[TransicionSalida]
    puede_editar_trabajo: bool
    puede_editar_recepcion: bool
    puede_asignar: bool
