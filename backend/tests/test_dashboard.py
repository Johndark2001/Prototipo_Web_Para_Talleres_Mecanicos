"""Dashboard mínimo (RF-14): conteos por estado y alertas de stock, solo del propio taller."""

import pytest

from tests.conftest import MECANICO, RECEPCION, cambiar


def test_conteos_por_estado_y_entregadas_hoy(abrir_orden, como, crear_vehiculo, ana):
    recibida = abrir_orden(con_mecanico=False)  # noqa: F841 (queda RECIBIDO)
    en_diagnostico = abrir_orden(vehiculo=crear_vehiculo(ana, "DEF456"))
    entregada = abrir_orden(vehiculo=crear_vehiculo(ana, "GHI789"))
    mecanico = como(MECANICO)
    cambiar(mecanico, en_diagnostico, "EN_DIAGNOSTICO")
    cambiar(mecanico, entregada, "EN_DIAGNOSTICO")
    mecanico.patch(f"/api/v1/ordenes/{entregada['id']}", json={"trabajo_realizado": "Listo"})
    cambiar(mecanico, entregada, "REPARADO")
    cambiar(como(RECEPCION), entregada, "ENTREGADO")

    datos = como(RECEPCION).get("/api/v1/dashboard").json()

    assert datos["ordenes_por_estado"] == {
        "RECIBIDO": 1,
        "EN_DIAGNOSTICO": 1,
        "ESPERANDO_REPUESTOS": 0,
        "REPARADO": 0,
    }
    assert datos["entregadas_hoy"] == 1


def test_alertas_de_stock_ordenadas_por_urgencia(como, equipo, taller_a, crear_repuesto):
    crear_repuesto(taller_a, "OK01", stock_actual="9", stock_minimo="2")
    crear_repuesto(taller_a, "BAJO", stock_actual="2", stock_minimo="3")
    crear_repuesto(taller_a, "AGOT", stock_actual="0", stock_minimo="4")
    crear_repuesto(taller_a, "INAC", stock_actual="0", stock_minimo="4", activo=False)

    datos = como(RECEPCION).get("/api/v1/dashboard").json()

    assert datos["stock_bajo_total"] == 2  # los inactivos no generan alerta
    assert [r["codigo"] for r in datos["stock_bajo"]] == ["AGOT", "BAJO"]


def test_solo_cuenta_lo_del_propio_taller(
    abrir_orden, como, taller_b, crear_usuario, crear_repuesto
):
    abrir_orden()
    crear_repuesto(taller_b, "BAJO", stock_actual="0", stock_minimo="1")
    crear_usuario(taller_b, "admin@b.co")

    datos = como("admin@b.co").get("/api/v1/dashboard").json()

    assert sum(datos["ordenes_por_estado"].values()) == 0
    assert datos["stock_bajo_total"] == 1


@pytest.mark.parametrize("email", [MECANICO])
def test_el_mecanico_usa_mis_ordenes_en_lugar_del_dashboard(como, equipo, email):
    assert como(email).get("/api/v1/dashboard").status_code == 403
