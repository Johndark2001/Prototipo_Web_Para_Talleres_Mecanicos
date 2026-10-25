"""Transiciones de estado de la orden (SPEC §7). Reglas puras, sin base de datos.

Las condiciones que dependen de los datos de la orden (RN-13, RN-17, RN-18 y la nota del
retroceso) se verifican en services/ordenes.py; aquí solo se decide qué cambio existe y
quién puede hacerlo.
"""

import enum
from dataclasses import dataclass

from app.models import ESTADOS_FINALES, EstadoOrden, RolUsuario

E = EstadoOrden


class TipoTransicion(enum.StrEnum):
    AVANCE = "AVANCE"
    ENTREGA = "ENTREGA"
    CANCELACION = "CANCELACION"
    RETROCESO = "RETROCESO"


@dataclass(frozen=True)
class Transicion:
    destino: EstadoOrden
    tipo: TipoTransicion

    @property
    def requiere_nota(self) -> bool:
        # RN-18 (motivo de cancelación) y la nota obligatoria al devolver la orden (§7).
        return self.tipo in (TipoTransicion.CANCELACION, TipoTransicion.RETROCESO)


# Cambios de taller: los hace el mecánico asignado o el ADMIN.
AVANCES_DE_TALLER = {
    E.RECIBIDO: (E.EN_DIAGNOSTICO,),
    E.EN_DIAGNOSTICO: (E.ESPERANDO_REPUESTOS, E.REPARADO),
    E.ESPERANDO_REPUESTOS: (E.REPARADO,),
}
ROLES_ENTREGAN_Y_CANCELAN = (RolUsuario.ADMIN, RolUsuario.RECEPCION)


def estado_anterior(
    estado: EstadoOrden, origen_de_reparado: EstadoOrden | None = None
) -> EstadoOrden | None:
    """Estado al que el ADMIN puede devolver la orden, un solo paso atrás.

    REPARADO vuelve al estado desde el que llegó (EN_DIAGNOSTICO o ESPERANDO_REPUESTOS).
    De ESPERANDO_REPUESTOS no se vuelve a EN_DIAGNOSTICO (H-1).
    """
    if estado == E.EN_DIAGNOSTICO:
        return E.RECIBIDO
    if estado == E.REPARADO:
        return origen_de_reparado or E.EN_DIAGNOSTICO
    return None


def transiciones_posibles(
    estado: EstadoOrden,
    rol: RolUsuario,
    es_mecanico_asignado: bool = False,
    origen_de_reparado: EstadoOrden | None = None,
) -> list[Transicion]:
    """Cambios que este usuario puede pedir desde `estado`, en el orden en que se muestran."""
    if estado in ESTADOS_FINALES:
        return []  # RN-07

    posibles: list[Transicion] = []
    if rol == RolUsuario.ADMIN or (rol == RolUsuario.MECANICO and es_mecanico_asignado):
        posibles += [
            Transicion(d, TipoTransicion.AVANCE) for d in AVANCES_DE_TALLER.get(estado, ())
        ]
    if rol in ROLES_ENTREGAN_Y_CANCELAN:
        if estado == E.REPARADO:
            posibles.append(Transicion(E.ENTREGADO, TipoTransicion.ENTREGA))
        posibles.append(Transicion(E.CANCELADA, TipoTransicion.CANCELACION))
    if rol == RolUsuario.ADMIN:
        anterior = estado_anterior(estado, origen_de_reparado)
        if anterior is not None:
            posibles.append(Transicion(anterior, TipoTransicion.RETROCESO))
    return posibles


def transicion_existe(
    estado: EstadoOrden, destino: EstadoOrden, origen_de_reparado: EstadoOrden | None = None
) -> bool:
    """Si algún rol puede hacer el cambio. Distingue "no tiene permiso" de "cambio inválido"."""
    return any(
        t.destino == destino
        for t in transiciones_posibles(estado, RolUsuario.ADMIN, True, origen_de_reparado)
    )
