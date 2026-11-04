import re
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.db import restriccion_violada
from app.core.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.models import ESTADOS_FINALES, Cliente, OrdenTrabajo, Usuario, Vehiculo
from app.schemas.clientes import ClienteActualizar, ClienteCrear

RESTRICCION_DOCUMENTO = "uq_cliente_taller_documento"
MENSAJE_DOCUMENTO_DUPLICADO = "Ya existe un cliente con ese documento en el taller"
# Campo del error cuando la placa llega dentro del alta del cliente (cambio #6).
CAMPO_PLACA = "vehiculo.placa"
MENSAJE_ANONIMIZADO = "Los datos de este cliente fueron anonimizados y ya no se pueden modificar"


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


def obtener(
    db: Session,
    actual: Usuario,
    cliente_id: int,
    con_vehiculos: bool = False,
    bloquear: bool = False,
) -> Cliente:
    # Un cliente de otro taller responde igual que uno inexistente (ADR-006).
    consulta = select(Cliente).where(
        Cliente.id == cliente_id, Cliente.taller_id == actual.taller_id
    )
    if con_vehiculos:
        consulta = consulta.options(
            selectinload(Cliente.vehiculos), joinedload(Cliente.anonimizador)
        )
    if bloquear:
        consulta = consulta.with_for_update()
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


def _guardar(db: Session, placa: str | None = None) -> None:
    try:
        db.commit()
    except IntegrityError as exc:  # dos registros simultáneos con el mismo documento o placa
        db.rollback()
        if restriccion_violada(exc) == RESTRICCION_DOCUMENTO:
            raise DatosInvalidos("documento", MENSAJE_DOCUMENTO_DUPLICADO) from exc
        if placa and (error := _vehiculos().error_placa_simultanea(exc, placa, CAMPO_PLACA)):
            raise error from exc
        raise


def _vehiculos():
    # Import diferido: el servicio de vehículos ya importa este módulo.
    from app.services import vehiculos

    return vehiculos


def crear(db: Session, actual: Usuario, datos: ClienteCrear) -> Cliente:
    """Alta del cliente y, si viene, de su primer vehículo en una sola transacción (#6)."""
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
    placa = None
    if datos.vehiculo is not None:
        placa = datos.vehiculo.placa
        _vehiculos().nuevo(db, actual, cliente, datos.vehiculo, campo=CAMPO_PLACA)
    _guardar(db, placa)
    return cliente


def actualizar(db: Session, actual: Usuario, cliente_id: int, datos: ClienteActualizar) -> Cliente:
    cliente = obtener(db, actual, cliente_id)
    if cliente.anonimizado:
        raise Conflicto(MENSAJE_ANONIMIZADO)
    cambios = datos.model_dump(exclude_unset=True)
    if "documento" in cambios:
        _verificar_documento_libre(db, actual, cambios["documento"], excepto_id=cliente.id)

    for campo, valor in cambios.items():
        setattr(cliente, campo, valor)
    _guardar(db)
    return cliente


def anonimizar(db: Session, actual: Usuario, cliente_id: int) -> Cliente:
    """Borra los datos personales del cliente y conserva su historia (RN-11, RNF-06).

    No borra filas: las órdenes, el historial y los carros siguen apuntando al mismo
    cliente, que queda inactivo con el nombre "Cliente anonimizado N.º <id>". La
    autorización y su fecha se conservan como prueba de que el dato se trató con permiso.
    """
    # El bloqueo evita que otra solicitud lo edite o le abra una orden al mismo tiempo.
    cliente = obtener(db, actual, cliente_id, bloquear=True)
    if cliente.anonimizado:
        raise Conflicto("Este cliente ya fue anonimizado")
    abiertas = db.scalar(
        select(func.count(OrdenTrabajo.id)).where(
            OrdenTrabajo.cliente_id == cliente.id,
            OrdenTrabajo.estado.not_in(ESTADOS_FINALES),
        )
    )
    if abiertas:
        raise Conflicto(
            "El cliente tiene órdenes abiertas. Entréguelas o cancélelas antes de anonimizarlo."
        )

    cliente.nombre = f"Cliente anonimizado N.º {cliente.id}"
    cliente.telefono = ""
    cliente.email = None
    cliente.documento = None
    cliente.activo = False
    cliente.anonimizado = True
    cliente.anonimizado_en = func.now()  # reloj de la base, como creado_en
    cliente.anonimizado_por = actual.id
    db.commit()
    return obtener(db, actual, cliente.id, con_vehiculos=True)
