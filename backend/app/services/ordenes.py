import secrets
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.db import restriccion_violada
from app.core.errores import Conflicto, DatosInvalidos, NoEncontrado, SinPermiso
from app.models import (
    ESTADOS_FINALES,
    AsignacionOrden,
    EstadoOrden,
    HistorialEstadoOrden,
    OrdenRepuesto,
    OrdenServicio,
    OrdenTrabajo,
    RolUsuario,
    Taller,
    Usuario,
    Vehiculo,
)
from app.schemas.ordenes import AsignacionCrear, CambioEstado, OrdenActualizar, OrdenCrear
from app.services import inventario as servicio_inventario
from app.services import usuarios as servicio_usuarios
from app.services import vehiculos as servicio_vehiculos
from app.services.flujo_orden import transicion_existe, transiciones_posibles

RESTRICCION_ORDEN_ABIERTA = "uq_orden_vehiculo_abierta"
CAMPOS_DEL_MECANICO = {"diagnostico", "trabajo_realizado"}
ROLES_RECEPCION = (RolUsuario.ADMIN, RolUsuario.RECEPCION)
NOMBRES_ESTADO = {
    EstadoOrden.RECIBIDO: "Recibido",
    EstadoOrden.EN_DIAGNOSTICO: "En diagnóstico",
    EstadoOrden.ESPERANDO_REPUESTOS: "Esperando repuestos",
    EstadoOrden.REPARADO: "Reparado",
    EstadoOrden.ENTREGADO: "Entregado",
    EstadoOrden.CANCELADA: "Cancelada",
}


def _visibles(actual: Usuario):
    """Filtro de lectura: siempre el taller (ADR-006) y, para el mecánico, sus órdenes (§3)."""
    filtros = [OrdenTrabajo.taller_id == actual.taller_id]
    if actual.rol == RolUsuario.MECANICO:
        filtros.append(OrdenTrabajo.mecanico_id == actual.id)
    return filtros


def listar(
    db: Session,
    actual: Usuario,
    page: int,
    page_size: int,
    estado: EstadoOrden | None = None,
    abiertas: bool | None = None,
    mecanico_id: int | None = None,
    vehiculo_id: int | None = None,
) -> tuple[list[OrdenTrabajo], int]:
    filtros = _visibles(actual)
    if estado is not None:
        filtros.append(OrdenTrabajo.estado == estado)
    if abiertas is True:
        filtros.append(OrdenTrabajo.estado.notin_(ESTADOS_FINALES))
    elif abiertas is False:
        filtros.append(OrdenTrabajo.estado.in_(ESTADOS_FINALES))
    if mecanico_id is not None:
        filtros.append(OrdenTrabajo.mecanico_id == mecanico_id)
    if vehiculo_id is not None:
        filtros.append(OrdenTrabajo.vehiculo_id == vehiculo_id)

    total = db.scalar(select(func.count()).select_from(OrdenTrabajo).where(*filtros)) or 0
    ordenes = db.scalars(
        select(OrdenTrabajo)
        .options(
            joinedload(OrdenTrabajo.vehiculo),
            joinedload(OrdenTrabajo.cliente),
            joinedload(OrdenTrabajo.mecanico),
        )
        .where(*filtros)
        .order_by(OrdenTrabajo.numero.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(ordenes), total


def obtener(db: Session, actual: Usuario, orden_id: int) -> OrdenTrabajo:
    orden = db.scalar(
        select(OrdenTrabajo)
        .options(
            joinedload(OrdenTrabajo.vehiculo),
            joinedload(OrdenTrabajo.cliente),
            joinedload(OrdenTrabajo.mecanico),
            joinedload(OrdenTrabajo.creador),
            selectinload(OrdenTrabajo.historial).joinedload(HistorialEstadoOrden.usuario),
            selectinload(OrdenTrabajo.asignaciones).options(
                joinedload(AsignacionOrden.mecanico), joinedload(AsignacionOrden.asignador)
            ),
            selectinload(OrdenTrabajo.servicios).joinedload(OrdenServicio.registrador),
            selectinload(OrdenTrabajo.repuestos).options(
                joinedload(OrdenRepuesto.repuesto), joinedload(OrdenRepuesto.registrador)
            ),
        )
        .where(OrdenTrabajo.id == orden_id, *_visibles(actual))
        # Tras un cambio, vuelve a leer el historial aunque la orden ya esté en la sesión.
        .execution_options(populate_existing=True)
    )
    if orden is None:
        raise NoEncontrado("La orden no existe")
    return orden


def obtener_bloqueada(db: Session, actual: Usuario, orden_id: int) -> OrdenTrabajo:
    """Bloquea la fila: dos cambios simultáneos no pueden partir del mismo estado.

    El bloqueo va en una consulta aparte porque PostgreSQL no admite FOR UPDATE sobre los
    joins opcionales (el mecánico puede ser nulo) con que `obtener` carga la orden.
    """
    bloqueada = db.scalar(
        select(OrdenTrabajo.id)
        .where(OrdenTrabajo.id == orden_id, *_visibles(actual))
        .with_for_update()
    )
    if bloqueada is None:
        raise NoEncontrado("La orden no existe")
    return obtener(db, actual, orden_id)


def _origen_de_reparado(orden: OrdenTrabajo) -> EstadoOrden | None:
    for registro in reversed(orden.historial):
        if registro.estado_nuevo == EstadoOrden.REPARADO:
            return registro.estado_anterior
    return None


def permisos(actual: Usuario, orden: OrdenTrabajo) -> dict:
    """Lo que la interfaz debe ofrecer a este usuario; el backend lo vuelve a verificar."""
    abierta = orden.estado not in ESTADOS_FINALES
    es_asignado = orden.mecanico_id == actual.id
    recepcion = actual.rol in ROLES_RECEPCION
    transiciones = transiciones_posibles(
        orden.estado, actual.rol, es_asignado, _origen_de_reparado(orden)
    )
    return {
        "transiciones": [
            {"estado": t.destino, "tipo": t.tipo, "requiere_nota": t.requiere_nota}
            for t in transiciones
        ],
        "puede_editar_trabajo": abierta and (recepcion or es_asignado),
        "puede_editar_recepcion": abierta and recepcion,
        "puede_asignar": abierta and recepcion,
    }


def exigir_abierta(orden: OrdenTrabajo) -> None:
    if orden.estado in ESTADOS_FINALES:  # RN-07
        estado = "entregada" if orden.estado == EstadoOrden.ENTREGADO else "cancelada"
        raise Conflicto(f"La orden #{orden.numero} ya fue {estado} y no se puede modificar")


def _mecanico_valido(db: Session, actual: Usuario, mecanico_id: int) -> Usuario:
    mecanico = servicio_usuarios.obtener(db, actual, mecanico_id)  # 404 si es de otro taller
    if mecanico.rol != RolUsuario.MECANICO or not mecanico.activo:
        raise DatosInvalidos("mecanico_id", "Elija un mecánico activo del taller")
    return mecanico


def _orden_abierta_del_vehiculo(db: Session, vehiculo: Vehiculo) -> OrdenTrabajo | None:
    return db.scalar(
        select(OrdenTrabajo).where(
            OrdenTrabajo.vehiculo_id == vehiculo.id, OrdenTrabajo.estado.notin_(ESTADOS_FINALES)
        )
    )


def _conflicto_orden_abierta(placa: str, abierta: OrdenTrabajo | None) -> Conflicto:
    # RN-08. El id permite a la interfaz ofrecer un enlace a la orden que ya existe.
    if abierta is None:
        return Conflicto(f"El carro {placa} ya tiene una orden abierta")
    return Conflicto(
        f"El carro {placa} ya tiene abierta la orden #{abierta.numero}",
        {"orden_id": abierta.id, "numero": abierta.numero},
    )


def crear(db: Session, actual: Usuario, datos: OrdenCrear) -> OrdenTrabajo:
    vehiculo = servicio_vehiculos.obtener(db, actual, datos.vehiculo_id)
    if not vehiculo.activo:
        raise DatosInvalidos("vehiculo_id", "El carro está inactivo. Actívelo antes de recibirlo.")
    if not vehiculo.cliente.activo:
        raise DatosInvalidos(
            "vehiculo_id", "El dueño del carro está inactivo. Actívelo antes de abrir la orden."
        )
    abierta = _orden_abierta_del_vehiculo(db, vehiculo)
    if abierta is not None:
        raise _conflicto_orden_abierta(vehiculo.placa, abierta)
    mecanico = _mecanico_valido(db, actual, datos.mecanico_id) if datos.mecanico_id else None

    # RN-12: el bloqueo de la fila del taller hace que dos recepciones simultáneas
    # no reciban el mismo número.
    taller = db.scalar(select(Taller).where(Taller.id == actual.taller_id).with_for_update())
    numero = taller.siguiente_numero_orden
    taller.siguiente_numero_orden = numero + 1

    orden = OrdenTrabajo(
        taller_id=actual.taller_id,
        numero=numero,
        vehiculo_id=vehiculo.id,
        cliente_id=vehiculo.cliente_id,
        mecanico_id=mecanico.id if mecanico else None,
        creado_por=actual.id,
        # 16 bytes = 128 bits aleatorios; 22 caracteres seguros para una URL (ADR-005).
        codigo_seguimiento=secrets.token_urlsafe(16),
        estado=EstadoOrden.RECIBIDO,
        kilometraje=datos.kilometraje,
        motivo_ingreso=datos.motivo_ingreso,
        fecha_entrega_estimada=datos.fecha_entrega_estimada,
    )
    orden.historial.append(
        HistorialEstadoOrden(estado_nuevo=EstadoOrden.RECIBIDO, usuario_id=actual.id)
    )
    if mecanico:
        orden.asignaciones.append(AsignacionOrden(mecanico_id=mecanico.id, asignado_por=actual.id))
    db.add(orden)
    try:
        db.commit()
    except IntegrityError as exc:  # otra recepción abrió una orden para el mismo carro
        db.rollback()
        if restriccion_violada(exc) == RESTRICCION_ORDEN_ABIERTA:
            raise _conflicto_orden_abierta(vehiculo.placa, None) from exc
        raise
    return obtener(db, actual, orden.id)


def actualizar(db: Session, actual: Usuario, orden_id: int, datos: OrdenActualizar) -> OrdenTrabajo:
    orden = obtener_bloqueada(db, actual, orden_id)
    exigir_abierta(orden)
    cambios = datos.model_dump(exclude_unset=True)
    if actual.rol == RolUsuario.MECANICO and set(cambios) - CAMPOS_DEL_MECANICO:
        raise SinPermiso("El mecánico solo registra el diagnóstico y el trabajo realizado")

    for campo, valor in cambios.items():
        setattr(orden, campo, valor)
    db.commit()
    return obtener(db, actual, orden.id)


def cambiar_estado(
    db: Session, actual: Usuario, orden_id: int, datos: CambioEstado
) -> OrdenTrabajo:
    orden = obtener_bloqueada(db, actual, orden_id)
    exigir_abierta(orden)
    destino = datos.estado
    if destino == orden.estado:
        raise Conflicto(f"La orden ya está en «{NOMBRES_ESTADO[destino]}»")

    origen_reparado = _origen_de_reparado(orden)
    transicion = next(
        (
            t
            for t in transiciones_posibles(
                orden.estado, actual.rol, orden.mecanico_id == actual.id, origen_reparado
            )
            if t.destino == destino
        ),
        None,
    )
    if transicion is None:
        if transicion_existe(orden.estado, destino, origen_reparado):
            raise SinPermiso(f"Su rol no puede pasar la orden a «{NOMBRES_ESTADO[destino]}»")
        raise Conflicto(
            f"No se puede pasar de «{NOMBRES_ESTADO[orden.estado]}» a «{NOMBRES_ESTADO[destino]}»"
        )
    if transicion.requiere_nota and not datos.nota:
        mensaje = (
            "Escriba el motivo de la cancelación"
            if destino == EstadoOrden.CANCELADA
            else "Escriba por qué devuelve la orden al estado anterior"
        )
        raise DatosInvalidos("nota", mensaje)
    if destino == EstadoOrden.EN_DIAGNOSTICO and orden.mecanico_id is None:  # RN-13
        raise Conflicto("Asigne un mecánico antes de iniciar el diagnóstico")
    if destino == EstadoOrden.REPARADO and not (orden.trabajo_realizado or "").strip():  # RN-17
        raise Conflicto("Escriba el trabajo realizado antes de marcar la orden como reparada")

    anterior = orden.estado
    orden.estado = destino
    if destino == EstadoOrden.ENTREGADO:
        orden.fecha_entrega = datetime.now(UTC)
    if destino == EstadoOrden.CANCELADA:
        orden.motivo_cancelacion = datos.nota  # RN-18
        # RN-03: los repuestos vuelven al estante. Las líneas se conservan como historia de la
        # orden; los movimientos DEVOLUCION explican el stock. Se bloquean en orden de id para
        # que dos cancelaciones simultáneas no se esperen mutuamente.
        for linea in sorted(orden.repuestos, key=lambda linea: linea.repuesto_id):
            servicio_inventario.devolver_a_stock(
                db,
                actual,
                linea.repuesto_id,
                linea.cantidad,
                orden,
                nota=f"Orden #{orden.numero} cancelada",
            )
    orden.historial.append(  # RN-01
        HistorialEstadoOrden(
            estado_anterior=anterior,
            estado_nuevo=destino,
            usuario_id=actual.id,
            nota=datos.nota,
        )
    )
    db.commit()
    return obtener(db, actual, orden.id)


def asignar(db: Session, actual: Usuario, orden_id: int, datos: AsignacionCrear) -> OrdenTrabajo:
    orden = obtener_bloqueada(db, actual, orden_id)
    exigir_abierta(orden)
    mecanico = _mecanico_valido(db, actual, datos.mecanico_id)
    if mecanico.id == orden.mecanico_id:
        raise DatosInvalidos("mecanico_id", f"La orden ya está asignada a {mecanico.nombre}")

    orden.mecanico_id = mecanico.id
    orden.asignaciones.append(  # RN-14
        AsignacionOrden(mecanico_id=mecanico.id, asignado_por=actual.id, nota=datos.nota)
    )
    db.commit()
    return obtener(db, actual, orden.id)
