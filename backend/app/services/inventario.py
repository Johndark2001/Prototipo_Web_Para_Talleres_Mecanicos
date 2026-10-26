"""Catálogo de repuestos y movimientos de stock (RF-08, RF-09, RF-10).

Todo cambio de stock pasa por `_mover_stock`: bloquea la fila del repuesto, deja un
movimiento con el stock resultante y nunca deja el stock negativo (RN-02, RN-11).
"""

from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.db import restriccion_violada
from app.core.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.models import MovimientoInventario, OrdenTrabajo, Repuesto, TipoMovimiento, Usuario
from app.schemas.inventario import MovimientoCrear, RepuestoActualizar, RepuestoCrear

RESTRICCION_CODIGO = "uq_repuesto_taller_codigo"
STOCK_BAJO = Repuesto.stock_actual <= Repuesto.stock_minimo  # RN-04


def formatear_cantidad(cantidad: Decimal) -> str:
    """2.00 → "2"; 1.50 → "1,5" (como se escribe en Colombia)."""
    return format(cantidad.normalize(), "f").replace(".", ",")


def listar(
    db: Session,
    actual: Usuario,
    page: int,
    page_size: int,
    buscar: str | None = None,
    stock_bajo: bool | None = None,
    activo: bool | None = None,
) -> tuple[list[Repuesto], int]:
    filtros = [Repuesto.taller_id == actual.taller_id]
    texto = (buscar or "").strip()
    if texto:
        filtros.append(
            or_(
                Repuesto.codigo.icontains(texto, autoescape=True),
                Repuesto.nombre.icontains(texto, autoescape=True),
            )
        )
    if stock_bajo is True:
        filtros.append(STOCK_BAJO)
    elif stock_bajo is False:
        filtros.append(~STOCK_BAJO)
    if activo is not None:
        filtros.append(Repuesto.activo == activo)

    total = db.scalar(select(func.count()).select_from(Repuesto).where(*filtros)) or 0
    repuestos = db.scalars(
        select(Repuesto)
        .where(*filtros)
        .order_by(Repuesto.nombre, Repuesto.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(repuestos), total


def obtener(db: Session, actual: Usuario, repuesto_id: int, bloquear: bool = False) -> Repuesto:
    consulta = select(Repuesto).where(
        Repuesto.id == repuesto_id, Repuesto.taller_id == actual.taller_id
    )
    if bloquear:
        # Dos movimientos simultáneos no pueden partir del mismo stock.
        consulta = consulta.with_for_update().execution_options(populate_existing=True)
    repuesto = db.scalar(consulta)
    if repuesto is None:  # ADR-006: un repuesto de otro taller responde igual que uno inexistente
        raise NoEncontrado("El repuesto no existe")
    return repuesto


def _mover_stock(
    db: Session,
    actual: Usuario,
    repuesto: Repuesto,
    tipo: TipoMovimiento,
    cantidad: Decimal,
    orden: OrdenTrabajo | None = None,
    nota: str | None = None,
) -> None:
    """Aplica un cambio de stock ya validado. `repuesto` debe venir bloqueado."""
    resultante = repuesto.stock_actual + cantidad
    if resultante < 0:  # RN-02; la restricción CHECK de la base es la segunda barrera
        raise Conflicto(
            f"No hay suficiente {repuesto.nombre}: quedan "
            f"{formatear_cantidad(repuesto.stock_actual)} {repuesto.unidad}",
            {"stock_actual": str(repuesto.stock_actual)},
        )
    repuesto.stock_actual = resultante
    db.add(
        MovimientoInventario(
            repuesto_id=repuesto.id,
            orden_id=orden.id if orden else None,
            usuario_id=actual.id,
            tipo=tipo,
            cantidad=cantidad,
            stock_resultante=resultante,
            nota=nota,
        )
    )


def _verificar_codigo_libre(
    db: Session, actual: Usuario, codigo: str, excepto_id: int | None = None
) -> None:
    consulta = select(Repuesto.id).where(
        Repuesto.taller_id == actual.taller_id, Repuesto.codigo == codigo
    )
    if excepto_id is not None:
        consulta = consulta.where(Repuesto.id != excepto_id)
    if db.scalar(consulta) is not None:
        raise DatosInvalidos("codigo", f"Ya existe un repuesto con el código {codigo}")


def _guardar(db: Session, codigo: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:  # dos registros simultáneos con el mismo código
        db.rollback()
        if restriccion_violada(exc) == RESTRICCION_CODIGO:
            raise DatosInvalidos("codigo", f"Ya existe un repuesto con el código {codigo}") from exc
        raise


def crear(db: Session, actual: Usuario, datos: RepuestoCrear) -> Repuesto:
    _verificar_codigo_libre(db, actual, datos.codigo)
    repuesto = Repuesto(
        taller_id=actual.taller_id,
        codigo=datos.codigo,
        nombre=datos.nombre,
        unidad=datos.unidad,
        precio_venta=datos.precio_venta,
        stock_minimo=datos.stock_minimo,
        stock_actual=Decimal(0),
    )
    db.add(repuesto)
    db.flush()
    if datos.stock_inicial > 0:
        # El stock inicial también queda como movimiento: el stock siempre se puede explicar.
        _mover_stock(
            db, actual, repuesto, TipoMovimiento.ENTRADA, datos.stock_inicial, nota="Stock inicial"
        )
    _guardar(db, datos.codigo)
    db.refresh(repuesto)
    return repuesto


def actualizar(
    db: Session, actual: Usuario, repuesto_id: int, datos: RepuestoActualizar
) -> Repuesto:
    repuesto = obtener(db, actual, repuesto_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "codigo" in cambios and cambios["codigo"] != repuesto.codigo:
        _verificar_codigo_libre(db, actual, cambios["codigo"], excepto_id=repuesto.id)
    # Cambiar el precio no altera las órdenes ya registradas: cada línea copió el suyo (RN-05).
    for campo, valor in cambios.items():
        setattr(repuesto, campo, valor)
    _guardar(db, repuesto.codigo)
    db.refresh(repuesto)
    return repuesto


def registrar_movimiento(
    db: Session, actual: Usuario, repuesto_id: int, datos: MovimientoCrear
) -> Repuesto:
    repuesto = obtener(db, actual, repuesto_id, bloquear=True)
    if not repuesto.activo:
        raise Conflicto("El repuesto está inactivo. Actívelo antes de moverle el stock.")

    if datos.tipo == TipoMovimiento.ENTRADA:
        if datos.cantidad is None:
            raise DatosInvalidos("cantidad", "Escriba cuántas unidades entraron")
        cambio = datos.cantidad
    else:
        if datos.stock_contado is None:
            raise DatosInvalidos("stock_contado", "Escriba cuántas unidades contó")
        if not datos.nota:
            raise DatosInvalidos("nota", "Escriba el motivo del ajuste")
        cambio = datos.stock_contado - repuesto.stock_actual
        if cambio == 0:
            actual_texto = formatear_cantidad(repuesto.stock_actual)
            raise DatosInvalidos(
                "stock_contado", f"El stock ya es {actual_texto}: no hay nada que ajustar"
            )

    _mover_stock(db, actual, repuesto, datos.tipo, cambio, nota=datos.nota)
    db.commit()
    db.refresh(repuesto)
    return repuesto


def listar_movimientos(
    db: Session, actual: Usuario, repuesto_id: int, page: int, page_size: int
) -> tuple[list[MovimientoInventario], int]:
    obtener(db, actual, repuesto_id)  # 404 si es de otro taller
    filtro = MovimientoInventario.repuesto_id == repuesto_id
    total = db.scalar(select(func.count()).select_from(MovimientoInventario).where(filtro)) or 0
    movimientos = db.scalars(
        select(MovimientoInventario)
        .options(joinedload(MovimientoInventario.usuario), joinedload(MovimientoInventario.orden))
        .where(filtro)
        .order_by(MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(movimientos), total


# --- Usados por las órdenes (RF-09) -------------------------------------------------------


def descontar_para_orden(
    db: Session, actual: Usuario, repuesto_id: int, cantidad: Decimal, orden: OrdenTrabajo
) -> Repuesto:
    repuesto = obtener(db, actual, repuesto_id, bloquear=True)
    if not repuesto.activo:
        raise DatosInvalidos("repuesto_id", "El repuesto está inactivo")
    _mover_stock(db, actual, repuesto, TipoMovimiento.SALIDA, -cantidad, orden=orden)
    return repuesto


def devolver_a_stock(
    db: Session,
    actual: Usuario,
    repuesto_id: int,
    cantidad: Decimal,
    orden: OrdenTrabajo,
    nota: str,
) -> None:
    """RN-03: el repuesto vuelve al estante aunque esté inactivo; el movimiento lo explica."""
    repuesto = obtener(db, actual, repuesto_id, bloquear=True)
    _mover_stock(db, actual, repuesto, TipoMovimiento.DEVOLUCION, cantidad, orden=orden, nota=nota)
