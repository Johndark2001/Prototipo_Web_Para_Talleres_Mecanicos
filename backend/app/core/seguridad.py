from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import obtener_configuracion

ALGORITMO_JWT = "HS256"

_hasher = PasswordHasher()  # argon2id con los parámetros recomendados por la biblioteca
# Se verifica contra este hash cuando el correo no existe, para que la respuesta
# tarde lo mismo y no revele qué correos están registrados.
_HASH_FICTICIO = _hasher.hash("clave-ficticia-para-igualar-tiempos")


def hashear_clave(clave: str) -> str:
    return _hasher.hash(clave)


def verificar_clave(hash_guardado: str | None, clave: str) -> bool:
    try:
        coincide = _hasher.verify(hash_guardado or _HASH_FICTICIO, clave)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    return coincide and hash_guardado is not None


def crear_token_sesion(usuario_id: int) -> str:
    config = obtener_configuracion()
    ahora = datetime.now(UTC)
    contenido = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(hours=config.sesion_horas),
    }
    return jwt.encode(contenido, config.secret_key, algorithm=ALGORITMO_JWT)


def leer_token_sesion(token: str) -> int | None:
    """Devuelve el id del usuario si el token es válido y no ha vencido."""
    try:
        contenido = jwt.decode(
            token,
            obtener_configuracion().secret_key,
            algorithms=[ALGORITMO_JWT],
            options={"require": ["exp", "sub"]},
        )
        return int(contenido["sub"])
    except (jwt.PyJWTError, ValueError):
        return None
