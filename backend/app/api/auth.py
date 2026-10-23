from fastapi import APIRouter, Response, status

from app.api.deps import DB, NOMBRE_COOKIE_SESION, UsuarioActual
from app.core.config import obtener_configuracion
from app.core.seguridad import crear_token_sesion
from app.models import Usuario
from app.schemas.usuarios import LoginEntrada, SesionSalida, TallerResumen, UsuarioSalida
from app.services import auth as servicio_auth

router = APIRouter(prefix="/auth", tags=["autenticación"])


def _sesion(usuario: Usuario) -> SesionSalida:
    return SesionSalida(
        usuario=UsuarioSalida.model_validate(usuario),
        taller=TallerResumen.model_validate(usuario.taller),
    )


def _atributos_cookie() -> dict:
    config = obtener_configuracion()
    return {
        "httponly": True,
        "secure": config.es_produccion,  # en desarrollo no hay HTTPS
        "samesite": "lax",
        "path": "/",
    }


@router.post("/login", response_model=SesionSalida)
def iniciar_sesion(datos: LoginEntrada, response: Response, db: DB) -> SesionSalida:
    usuario = servicio_auth.autenticar(db, datos.email, datos.password)
    response.set_cookie(
        NOMBRE_COOKIE_SESION,
        crear_token_sesion(usuario.id),
        max_age=obtener_configuracion().sesion_horas * 3600,
        **_atributos_cookie(),
    )
    return _sesion(usuario)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion() -> Response:
    respuesta = Response(status_code=status.HTTP_204_NO_CONTENT)
    respuesta.delete_cookie(NOMBRE_COOKIE_SESION, **_atributos_cookie())
    return respuesta


@router.get("/me", response_model=SesionSalida)
def sesion_actual(usuario: UsuarioActual) -> SesionSalida:
    return _sesion(usuario)
