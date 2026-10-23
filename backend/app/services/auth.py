from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import NoAutenticado
from app.core.seguridad import verificar_clave
from app.models import Usuario

# Mensaje genérico: no revela si falló el correo o la clave (ADR-005).
MENSAJE_CREDENCIALES = "Correo o clave incorrectos"


def autenticar(db: Session, email: str, clave: str) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    clave_valida = verificar_clave(usuario.password_hash if usuario else None, clave)
    if usuario is None or not clave_valida or not usuario.activo or not usuario.taller.activo:
        raise NoAutenticado(MENSAJE_CREDENCIALES)

    usuario.ultimo_acceso = datetime.now(UTC)
    db.commit()
    return usuario


def usuario_de_sesion(db: Session, usuario_id: int | None) -> Usuario:
    """Relee al usuario en cada solicitud: si lo desactivan, pierde el acceso al instante."""
    usuario = db.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None or not usuario.activo or not usuario.taller.activo:
        raise NoAutenticado("Su sesión no es válida. Inicie sesión de nuevo.")
    return usuario
