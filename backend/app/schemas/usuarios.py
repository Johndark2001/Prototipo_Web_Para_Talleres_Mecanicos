from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from app.models import RolUsuario
from app.schemas.comunes import Clave, Nombre


class LoginEntrada(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    rol: RolUsuario
    activo: bool
    ultimo_acceso: datetime | None
    creado_en: datetime


class TallerResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class SesionSalida(BaseModel):
    usuario: UsuarioSalida
    taller: TallerResumen


class UsuarioCrear(BaseModel):
    nombre: Nombre
    email: EmailStr
    password: Clave
    rol: RolUsuario


class UsuarioActualizar(BaseModel):
    """Actualización parcial: solo cambian los campos enviados."""

    nombre: Nombre | None = None
    rol: RolUsuario | None = None
    activo: bool | None = None
