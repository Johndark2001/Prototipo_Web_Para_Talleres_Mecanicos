"""Formato único de error de la API (SPEC §10): {"error": {"code", "message", "details"}}."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorAplicacion(Exception):
    status_code = 400
    code = "ERROR"

    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.message = message
        self.details = details


class NoAutenticado(ErrorAplicacion):
    status_code = 401
    code = "NO_AUTENTICADO"


class SinPermiso(ErrorAplicacion):
    status_code = 403
    code = "SIN_PERMISO"


class NoEncontrado(ErrorAplicacion):
    status_code = 404
    code = "NO_ENCONTRADO"


class DatosInvalidos(ErrorAplicacion):
    """Dato que solo la base puede validar (p. ej. placa repetida). Mismo formato que Pydantic."""

    status_code = 422
    code = "DATOS_INVALIDOS"

    def __init__(self, campo: str, mensaje: str):
        super().__init__("Revise los datos enviados", [{"campo": campo, "mensaje": mensaje}])


class Conflicto(ErrorAplicacion):
    status_code = 409
    code = "CONFLICTO"


class DemasiadasSolicitudes(ErrorAplicacion):
    status_code = 429
    code = "DEMASIADAS_SOLICITUDES"


class ServicioNoDisponible(ErrorAplicacion):
    status_code = 503
    code = "SERVICIO_NO_DISPONIBLE"


def cuerpo_error(code: str, message: str, details: Any = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


# Tipo de los PydanticCustomError de app/schemas: su mensaje ya está en español.
TIPO_ERROR_PROPIO = "dato_invalido"

_MENSAJES_HTTP = {
    404: ("NO_ENCONTRADO", "Recurso no encontrado"),
    405: ("METODO_NO_PERMITIDO", "Método no permitido"),
}


def _mensaje_validacion(error: dict) -> str:
    """Traduce los errores de Pydantic al español del taller (RNF-08)."""
    tipo = error.get("type", "")
    contexto = error.get("ctx") or {}
    if tipo == TIPO_ERROR_PROPIO:
        return error["msg"]
    if tipo == "missing":
        return "Este campo es obligatorio"
    if tipo == "string_too_short":
        return f"Debe tener al menos {contexto.get('min_length')} caracteres"
    if tipo == "string_too_long":
        return f"Debe tener máximo {contexto.get('max_length')} caracteres"
    if tipo == "enum":
        return "Opción no válida"
    if tipo == "value_error" and "email" in str(error.get("msg", "")).lower():
        return "Correo no válido"
    if tipo == "greater_than_equal":
        return f"Debe ser mayor o igual a {contexto.get('ge')}"
    if tipo == "less_than_equal":
        return f"Debe ser menor o igual a {contexto.get('le')}"
    if tipo in ("int_parsing", "int_type", "int_from_float"):
        return "Debe ser un número entero"
    if tipo == "greater_than":
        return f"Debe ser mayor que {contexto.get('gt')}"
    if tipo in ("decimal_parsing", "decimal_type"):
        return "Debe ser un número"
    if tipo == "decimal_max_places":
        return f"Use máximo {contexto.get('decimal_places')} decimales"
    if tipo in ("decimal_max_digits", "decimal_whole_digits"):
        return "El número es demasiado grande"
    return "Valor no válido"


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorAplicacion)
    async def _error_aplicacion(_: Request, exc: ErrorAplicacion) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content=cuerpo_error(exc.code, exc.message, exc.details)
        )

    @app.exception_handler(RequestValidationError)
    async def _error_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        detalles = [
            {
                "campo": ".".join(str(parte) for parte in err["loc"] if parte != "body"),
                "mensaje": _mensaje_validacion(err),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=cuerpo_error("DATOS_INVALIDOS", "Revise los datos enviados", detalles),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _error_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, message = _MENSAJES_HTTP.get(exc.status_code, ("ERROR", "Solicitud no válida"))
        return JSONResponse(status_code=exc.status_code, content=cuerpo_error(code, message))

    @app.exception_handler(Exception)
    async def _error_inesperado(_: Request, exc: Exception) -> JSONResponse:
        # El detalle va al log del servidor, nunca al usuario.
        logger.exception("Error no controlado", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=cuerpo_error("ERROR_INTERNO", "Ocurrió un error inesperado. Intente de nuevo."),
        )
