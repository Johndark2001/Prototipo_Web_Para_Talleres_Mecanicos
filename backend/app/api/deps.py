from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import obtener_db
from app.core.errores import SinPermiso
from app.core.seguridad import leer_token_sesion
from app.models import RolUsuario, Usuario
from app.services import auth as servicio_auth

NOMBRE_COOKIE_SESION = "sesion"

DB = Annotated[Session, Depends(obtener_db)]


def obtener_usuario_actual(request: Request, db: DB) -> Usuario:
    token = request.cookies.get(NOMBRE_COOKIE_SESION)
    usuario_id = leer_token_sesion(token) if token else None
    return servicio_auth.usuario_de_sesion(db, usuario_id)


UsuarioActual = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requiere_roles(*roles: RolUsuario):
    """El rol siempre se lee de la base de datos, nunca de lo que envía el cliente (ADR-005)."""

    def verificar(usuario: UsuarioActual) -> Usuario:
        if usuario.rol not in roles:
            raise SinPermiso("Su rol no tiene permiso para esta acción")
        return usuario

    return verificar


SoloAdmin = Annotated[Usuario, Depends(requiere_roles(RolUsuario.ADMIN))]
