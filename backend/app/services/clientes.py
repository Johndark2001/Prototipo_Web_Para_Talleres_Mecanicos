import re
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.db import restriccion_violada
from app.core.errores import DatosInvalidos, NoEncontrado
from app.models import Cliente, Usuario, Vehiculo
from app.schemas.clientes import ClienteActualizar, ClienteCrear

RESTRICCION_DOCUMENTO = "uq_cliente_taller_documento"
MENSAJE_DOCUMENTO_DUPLICADO = "Ya existe un cliente con ese documento en el taller"


def listar(
    db: Session,
    actual: Usuario,
    page: int,
    page_size: int,
    q: str | None = None,
    activo: bool | None = None,
) -> tuple[list[tuple[Cliente, int]], int]:
    """Clientes del taller con sus carros activos. `q` busca por nombre, teléfono o documento."""
    filtros = [Cliente.taller_id == actual.taller_id]
    if activo is not None:
        filtros.append(Cliente.activo == activo)
    texto = (q or "").strip()
    if texto:
        criterios = [
            Cliente.nombre.icontains(texto, autoescape=True),
            Cliente.documento.icontains(re.sub(r"[\s\-.]", "", texto), autoescape=True),
        ]
        digitos = re.sub(r"\D", "", texto)
        if digitos:
            criterios.append(Cliente.telefono.contains(digitos, autoescape=True))
        filtros.append(or_(*criterios))

    total = db.scalar(select(func.count()).select_from(Cliente).where(*filtros)) or 0
    total_vehiculos = (
        select(func.count(Vehiculo.id))
        .where(Vehiculo.cliente_id == Cliente.id, Vehiculo.activo)
        .correlate(Cliente)
        .scalar_subquery()
    )
    filas = db.execute(
        select(Cliente, total_vehiculos)
        .where(*filtros)
        .order_by(Cliente.nombre, Cliente.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return [(cliente, cantidad) for cliente, cantidad in filas], total


def obtener(db: Session, actual: Usuario, cliente_id: int, con_vehiculos: bool = False) -> Cliente:
    # Un cliente de otro taller responde igual que uno inexistente (ADR-006).
    consulta = select(Cliente).where(
        Cliente.id == cliente_id, Cliente.taller_id == actual.taller_id
    )
    if con_vehiculos:
        consulta = consulta.options(selectinload(Cliente.vehiculos))
    cliente = db.scalar(consulta)
    if cliente is None:
        raise NoEncontrado("El cliente no existe")
    return cliente


def _verificar_documento_libre(
    db: Session, actual: Usuario, documento: str | None, excepto_id: int | None = None
) -> None:
    if documento is None:
        return
    consulta = select(Cliente.id).where(
        Cliente.taller_id == actual.taller_id, Cliente.documento == documento
    )
    if excepto_id is not None:
        consulta = consulta.where(Cliente.id != excepto_id)
    if db.scalar(consulta) is not None:
        raise DatosInvalidos("documento", MENSAJE_DOCUMENTO_DUPLICADO)


def _guardar(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:  # dos registros simultáneos con el mismo documento
        db.rollback()
        if restriccion_violada(exc) == RESTRICCION_DOCUMENTO:
            raise DatosInvalidos("documento", MENSAJE_DOCUMENTO_DUPLICADO) from exc
        raise


def crear(db: Session, actual: Usuario, datos: ClienteCrear) -> Cliente:
    _verificar_documento_libre(db, actual, datos.documento)
    cliente = Cliente(
        taller_id=actual.taller_id,
        nombre=datos.nombre,
        telefono=datos.telefono,
        email=datos.email,
        documento=datos.documento,
        autoriza_datos=datos.autoriza_datos,
        fecha_autorizacion=datetime.now(UTC),
    )
    db.add(cliente)
    _guardar(db)
    return cliente


def actualizar(db: Session, actual: Usuario, cliente_id: int, datos: ClienteActualizar) -> Cliente:
    cliente = obtener(db, actual, cliente_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "documento" in cambios:
        _verificar_documento_libre(db, actual, cambios["documento"], excepto_id=cliente.id)

    for campo, valor in cambios.items():
        setattr(cliente, campo, valor)
    _guardar(db)
    return cliente
