"""Reglas de transición del SPEC §7, sin base de datos."""

import pytest

from app.models import EstadoOrden as E
from app.models import RolUsuario as R
from app.services.flujo_orden import (
    TipoTransicion,
    estado_anterior,
    transicion_existe,
    transiciones_posibles,
)


def destinos(estado, rol, asignado=False, origen=None) -> set[E]:
    return {t.destino for t in transiciones_posibles(estado, rol, asignado, origen)}


@pytest.mark.parametrize(
    ("desde", "hacia"),
    [
        (E.RECIBIDO, E.EN_DIAGNOSTICO),
        (E.EN_DIAGNOSTICO, E.ESPERANDO_REPUESTOS),
        (E.EN_DIAGNOSTICO, E.REPARADO),  # ESPERANDO_REPUESTOS es opcional (H-1)
        (E.ESPERANDO_REPUESTOS, E.REPARADO),
    ],
)
def test_mecanico_asignado_y_admin_hacen_los_cambios_de_taller(desde, hacia):
    assert hacia in destinos(desde, R.MECANICO, asignado=True)
    assert hacia in destinos(desde, R.ADMIN)
    assert hacia not in destinos(desde, R.MECANICO, asignado=False)
    assert hacia not in destinos(desde, R.RECEPCION)


def test_entregar_solo_desde_reparado_por_admin_o_recepcion():
    for rol in (R.ADMIN, R.RECEPCION):
        assert E.ENTREGADO in destinos(E.REPARADO, rol)
    assert E.ENTREGADO not in destinos(E.REPARADO, R.MECANICO, asignado=True)
    for estado in (E.RECIBIDO, E.EN_DIAGNOSTICO, E.ESPERANDO_REPUESTOS):
        assert not transicion_existe(estado, E.ENTREGADO)


@pytest.mark.parametrize(
    "estado", [E.RECIBIDO, E.EN_DIAGNOSTICO, E.ESPERANDO_REPUESTOS, E.REPARADO]
)
def test_cancelar_desde_cualquier_estado_no_final(estado):
    assert E.CANCELADA in destinos(estado, R.ADMIN)
    assert E.CANCELADA in destinos(estado, R.RECEPCION)
    assert E.CANCELADA not in destinos(estado, R.MECANICO, asignado=True)


@pytest.mark.parametrize("final", [E.ENTREGADO, E.CANCELADA])
def test_estados_finales_no_tienen_salida(final):
    # RN-07
    for rol in R:
        assert transiciones_posibles(final, rol, True) == []


@pytest.mark.parametrize(
    ("desde", "hacia"),
    [
        (E.RECIBIDO, E.REPARADO),
        (E.RECIBIDO, E.ESPERANDO_REPUESTOS),
        (E.ESPERANDO_REPUESTOS, E.RECIBIDO),
        (E.REPARADO, E.RECIBIDO),
    ],
)
def test_saltos_invalidos_no_existen_para_nadie(desde, hacia):
    assert not transicion_existe(desde, hacia)


def test_no_se_vuelve_de_esperando_repuestos_a_diagnostico_ni_siendo_admin():
    # H-1: la regla de "un paso atrás" no aplica a esta transición.
    assert estado_anterior(E.ESPERANDO_REPUESTOS) is None
    assert not transicion_existe(E.ESPERANDO_REPUESTOS, E.EN_DIAGNOSTICO)


@pytest.mark.parametrize(
    ("estado", "origen", "esperado"),
    [
        (E.EN_DIAGNOSTICO, None, E.RECIBIDO),
        (E.REPARADO, E.EN_DIAGNOSTICO, E.EN_DIAGNOSTICO),
        (E.REPARADO, E.ESPERANDO_REPUESTOS, E.ESPERANDO_REPUESTOS),
        (E.RECIBIDO, None, None),
    ],
)
def test_retroceso_de_un_paso_vuelve_al_estado_de_origen(estado, origen, esperado):
    assert estado_anterior(estado, origen) == esperado


def test_solo_el_admin_retrocede_y_siempre_con_nota():
    retrocesos = [
        t
        for t in transiciones_posibles(E.EN_DIAGNOSTICO, R.ADMIN)
        if t.tipo == TipoTransicion.RETROCESO
    ]
    assert [t.destino for t in retrocesos] == [E.RECIBIDO]
    assert retrocesos[0].requiere_nota
    assert E.RECIBIDO not in destinos(E.EN_DIAGNOSTICO, R.RECEPCION)
    assert E.RECIBIDO not in destinos(E.EN_DIAGNOSTICO, R.MECANICO, asignado=True)


def test_la_cancelacion_exige_motivo():
    # RN-18
    cancelacion = next(
        t for t in transiciones_posibles(E.RECIBIDO, R.RECEPCION) if t.destino == E.CANCELADA
    )
    assert cancelacion.requiere_nota
