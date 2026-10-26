from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    auth,
    clientes,
    dashboard,
    mecanicos,
    ordenes,
    repuestos,
    salud,
    seguimiento,
    usuarios,
    vehiculos,
)
from app.core.errores import NoEncontrado, cuerpo_error, registrar_manejadores

# En producción el backend sirve la interfaz compilada desde el mismo dominio (ADR-001).
DIRECTORIO_FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "dist"
METODOS_QUE_MODIFICAN = {"POST", "PUT", "PATCH", "DELETE"}


async def exigir_json_en_modificaciones(request: Request, call_next):
    """Parte de la defensa CSRF de ADR-005: un formulario de otro sitio no puede enviar JSON."""
    if request.method in METODOS_QUE_MODIFICAN and request.url.path.startswith("/api/"):
        tipo = request.headers.get("content-type", "")
        if not tipo.startswith("application/json"):
            return JSONResponse(
                status_code=415,
                content=cuerpo_error(
                    "TIPO_NO_SOPORTADO", "Las solicitudes deben enviarse en formato JSON"
                ),
            )
    return await call_next(request)


def montar_frontend(app: FastAPI, directorio: Path) -> None:
    if not directorio.is_dir():
        return
    app.mount("/assets", StaticFiles(directory=directorio / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def aplicacion_web(ruta: str) -> FileResponse:
        if ruta.startswith("api/"):
            raise NoEncontrado("Recurso no encontrado")
        archivo = (directorio / ruta).resolve()
        if ruta and archivo.is_file() and archivo.is_relative_to(directorio):
            return FileResponse(archivo)
        # Las rutas del frontend (/usuarios, /login…) las resuelve React Router.
        return FileResponse(directorio / "index.html")


def crear_app() -> FastAPI:
    app = FastAPI(
        title="Taller Digital — API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    registrar_manejadores(app)
    app.middleware("http")(exigir_json_en_modificaciones)

    api = APIRouter(prefix="/api/v1")
    api.include_router(salud.router)
    api.include_router(auth.router)
    api.include_router(usuarios.router)
    api.include_router(clientes.router)
    api.include_router(vehiculos.router)
    api.include_router(ordenes.router)
    api.include_router(mecanicos.router)
    api.include_router(repuestos.router)
    api.include_router(dashboard.router)
    api.include_router(seguimiento.router)
    app.include_router(api)

    montar_frontend(app, DIRECTORIO_FRONTEND)
    return app


app = crear_app()
