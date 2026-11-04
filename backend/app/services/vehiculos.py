from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.db import restriccion_violada
from app.core.errores import DatosInvalidos, NoEncontrado
from app.models import Cliente, TipoVehiculo, Usuario, Vehiculo
from app.schemas.vehiculos import (
    VehiculoActualizar,
    VehiculoCrear,
    VehiculoDatos,
    normalizar_placa,
)
from app.services import clientes as servicio_clientes

RESTRICCION_PLACA = "uq_vehiculo_taller_placa"


def _mensaje_placa_duplicada(placa: str, activo: bool = True) -> str:
    if activo:
        return f"Ya existe un carro con la placa {placa} en el taller"
    return f"La placa {placa} es de un carro inactivo: actívelo en lugar de registrarlo de nuevo"


def listar(
    db: Session,
    actual: Usuario,
    page: int,
    page_size: int,
    placa: str | None = None,
    cliente_id: int | None = None,
    activo: bool | None = None,
    tipo: TipoVehiculo | None = None,
) -> tuple[list[Vehiculo], int]:
    filtros = [Vehiculo.taller_id == actual.taller_id]
    orden = [Vehiculo.placa, Vehiculo.id]
    texto = normalizar_placa(placa or "")
    if texto:
        # Búsqueda parcial ("ABC" o "123") para autocompletar; la coincidencia exacta va primero.
        filtros.append(Vehiculo.placa.contains(texto, autoescape=True))
        orden.insert(0, (Vehiculo.placa == texto).desc())
    if cliente_id is not None:
        filtros.append(Vehiculo.cliente_id == cliente_id)
    if activo is not None:
        filtros.append(Vehiculo.activo == activo)
    if tipo is not None:
        filtros.append(Vehiculo.tipo == tipo)

    total = db.scalar(select(func.count()).select_from(Vehiculo).where(*filtros)) or 0
    vehiculos = db.scalars(
        select(Vehiculo)
        .options(joinedload(Vehiculo.cliente))
        .where(*filtros)
        .order_by(*orden)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(vehiculos), total


def obtener(db: Session, actual: Usuario, vehiculo_id: int) -> Vehiculo:
    vehiculo = db.scalar(
        select(Vehiculo)
        .options(joinedload(Vehiculo.cliente))
        .where(Vehiculo.id == vehiculo_id, Vehiculo.taller_id == actual.taller_id)
    )
    if vehiculo is None:
        raise NoEncontrado("El carro no existe")
    return vehiculo


def _dueno_valido(db: Session, actual: Usuario, cliente_id: int) -> Cliente:
    # ADR-006 punto 3: un cliente de otro taller responde 404, como si no existiera.
    cliente = servicio_clientes.obtener(db, actual, cliente_id)
    if not cliente.activo:
        raise DatosInvalidos(
            "cliente_id", "El cliente está inactivo. Actívelo antes de asociarle un carro."
        )
    return cliente


def _verificar_placa_libre(
    db: Session, actual: Usuario, placa: str, excepto_id: int | None = None, campo: str = "placa"
) -> None:
    consulta = select(Vehiculo.activo).where(
        Vehiculo.taller_id == actual.taller_id, Vehiculo.placa == placa
    )
    if excepto_id is not None:
        consulta = consulta.where(Vehiculo.id != excepto_id)
    activo = db.scalar(consulta)
    if activo is not None:
        raise DatosInvalidos(campo, _mensaje_placa_duplicada(placa, activo))


def error_placa_simultanea(exc: IntegrityError, placa: str, campo: str = "placa"):
    """Dos registros simultáneos de la misma placa: el segundo choca con la restricción."""
    if restriccion_violada(exc) == RESTRICCION_PLACA:
        return DatosInvalidos(campo, _mensaje_placa_duplicada(placa))
    return None


def _guardar(db: Session, placa: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if error := error_placa_simultanea(exc, placa):
            raise error from exc
        raise


def nuevo(
    db: Session, actual: Usuario, cliente: Cliente, datos: VehiculoDatos, campo: str = "placa"
) -> Vehiculo:
    """Agrega el vehículo a la sesión sin confirmar; quien llama hace el commit."""
    _verificar_placa_libre(db, actual, datos.placa, campo=campo)
    vehiculo = Vehiculo(
        taller_id=actual.taller_id,
        cliente=cliente,
        placa=datos.placa,
        tipo=datos.tipo,
        marca=datos.marca,
        modelo=datos.modelo,
        anio=datos.anio,
        color=datos.color,
    )
    db.add(vehiculo)
    return vehiculo


def crear(db: Session, actual: Usuario, datos: VehiculoCrear) -> Vehiculo:
    cliente = _dueno_valido(db, actual, datos.cliente_id)
    vehiculo = nuevo(db, actual, cliente, datos)
    _guardar(db, datos.placa)
    return vehiculo


def actualizar(
    db: Session, actual: Usuario, vehiculo_id: int, datos: VehiculoActualizar
) -> Vehiculo:
    vehiculo = obtener(db, actual, vehiculo_id)
    cambios = datos.model_dump(exclude_unset=True)

    # Cambiar de dueño no toca las órdenes anteriores: cada orden guarda su propio cliente.
    nuevo_dueno_id = cambios.pop("cliente_id", vehiculo.cliente_id)
    if nuevo_dueno_id != vehiculo.cliente_id:
        vehiculo.cliente = _dueno_valido(db, actual, nuevo_dueno_id)
    if "placa" in cambios and cambios["placa"] != vehiculo.placa:
        _verificar_placa_libre(db, actual, cambios["placa"], excepto_id=vehiculo.id)

    for campo, valor in cambios.items():
        setattr(vehiculo, campo, valor)
    _guardar(db, vehiculo.placa)
    return vehiculo
