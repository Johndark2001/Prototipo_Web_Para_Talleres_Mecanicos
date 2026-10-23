from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, NoEncontrado
from app.core.seguridad import hashear_clave
from app.models import RolUsuario, Usuario
from app.schemas.usuarios import UsuarioActualizar, UsuarioCrear

MENSAJE_CORREO_DUPLICADO = "Ya existe un usuario con ese correo"


def listar(
    db: Session,
    actual: Usuario,
    page: int,
    page_size: int,
    rol: RolUsuario | None = None,
    activo: bool | None = None,
) -> tuple[list[Usuario], int]:
    filtros = [Usuario.taller_id == actual.taller_id]
    if rol is not None:
        filtros.append(Usuario.rol == rol)
    if activo is not None:
        filtros.append(Usuario.activo == activo)

    total = db.scalar(select(func.count()).select_from(Usuario).where(*filtros)) or 0
    usuarios = db.scalars(
        select(Usuario)
        .where(*filtros)
        .order_by(Usuario.nombre, Usuario.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(usuarios), total


def obtener(db: Session, actual: Usuario, usuario_id: int) -> Usuario:
    # Un usuario de otro taller responde igual que uno inexistente (ADR-006).
    usuario = db.scalar(
        select(Usuario).where(Usuario.id == usuario_id, Usuario.taller_id == actual.taller_id)
    )
    if usuario is None:
        raise NoEncontrado("El usuario no existe")
    return usuario


def crear(db: Session, actual: Usuario, datos: UsuarioCrear) -> Usuario:
    email = datos.email.strip().lower()
    if db.scalar(select(Usuario.id).where(Usuario.email == email)) is not None:
        raise Conflicto(MENSAJE_CORREO_DUPLICADO)

    usuario = Usuario(
        taller_id=actual.taller_id,
        nombre=datos.nombre,
        email=email,
        password_hash=hashear_clave(datos.password),
        rol=datos.rol,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:  # dos altas simultáneas con el mismo correo
        db.rollback()
        raise Conflicto(MENSAJE_CORREO_DUPLICADO) from exc
    return usuario


def actualizar(db: Session, actual: Usuario, usuario_id: int, datos: UsuarioActualizar) -> Usuario:
    usuario = obtener(db, actual, usuario_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

    # Evita que el taller se quede sin administrador por un error propio.
    if usuario.id == actual.id and (
        cambios.get("activo") is False or cambios.get("rol", usuario.rol) != usuario.rol
    ):
        raise Conflicto("No puede cambiar su propio rol ni desactivar su propia cuenta")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    db.commit()
    return usuario
