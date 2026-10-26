"""Repuestos y mano de obra en la orden (RF-09), stock (RN-02, RN-03, RN-05) y liquidación
(RF-12, RN-06)."""

from decimal import Decimal

import pytest

from app.models import MovimientoInventario, Repuesto, TipoMovimiento
from tests.conftest import (
    ADMIN,
    MECANICO,
    OTRO_MECANICO,
    RECEPCION,
    borrar,
    cambiar,
    codigo_error,
)


@pytest.fixture
def filtro(taller_a, crear_repuesto):
    return crear_repuesto(taller_a, "W712", precio_venta="25000", stock_actual="10")


@pytest.fixture
def aceite(taller_a, crear_repuesto):
    return crear_repuesto(
        taller_a,
        "ACE20W50",
        nombre="Aceite 20W-50",
        unidad="litro",
        precio_venta="32333",
        stock_actual="8",
    )


def agregar_repuesto(cliente, orden, repuesto, cantidad):
    return cliente.post(
        f"/api/v1/ordenes/{orden['id']}/repuestos",
        json={"repuesto_id": repuesto.id, "cantidad": str(cantidad)},
    )


def agregar_servicio(cliente, orden, descripcion="Cambio de aceite", precio="40000", cantidad=1):
    return cliente.post(
        f"/api/v1/ordenes/{orden['id']}/servicios",
        json={"descripcion": descripcion, "precio_unitario": precio, "cantidad": str(cantidad)},
    )


def stock(db, repuesto) -> Decimal:
    db.expire_all()
    return db.get(Repuesto, repuesto.id).stock_actual


def movimientos(db, repuesto) -> list[MovimientoInventario]:
    db.expire_all()
    return (
        db.query(MovimientoInventario)
        .filter_by(repuesto_id=repuesto.id)
        .order_by(MovimientoInventario.id)
        .all()
    )


# --- Repuestos en la orden (RF-09) -------------------------------------------------------------


def test_agregar_repuesto_descuenta_stock_y_registra_la_salida(
    db, abrir_orden, como, filtro, equipo
):
    orden = abrir_orden()

    respuesta = agregar_repuesto(como(MECANICO), orden, filtro, 2)

    assert respuesta.status_code == 201, respuesta.text
    [linea] = respuesta.json()["repuestos"]
    assert linea["repuesto"]["codigo"] == "W712"
    assert Decimal(linea["cantidad"]) == 2
    assert Decimal(linea["precio_unitario"]) == 25000
    assert Decimal(linea["subtotal"]) == 50000
    assert linea["registrador"]["id"] == equipo["mecanico"].id  # RN-15
    assert stock(db, filtro) == 8
    [salida] = movimientos(db, filtro)
    assert salida.tipo == TipoMovimiento.SALIDA
    assert salida.cantidad == -2
    assert salida.stock_resultante == 8
    assert salida.orden_id == orden["id"]


def test_stock_insuficiente_responde_409_y_no_cambia_nada(db, abrir_orden, como, filtro):
    orden = abrir_orden()

    respuesta = agregar_repuesto(como(RECEPCION), orden, filtro, 11)

    assert respuesta.status_code == 409
    assert "quedan 10 unidad" in respuesta.json()["error"]["message"]
    assert stock(db, filtro) == 10
    assert movimientos(db, filtro) == []
    detalle = como(RECEPCION).get(f"/api/v1/ordenes/{orden['id']}").json()
    assert detalle["repuestos"] == []


def test_se_puede_usar_todo_el_stock_hasta_cero(db, abrir_orden, como, filtro):
    orden = abrir_orden()
    assert agregar_repuesto(como(RECEPCION), orden, filtro, 10).status_code == 201
    assert stock(db, filtro) == 0
    assert agregar_repuesto(como(RECEPCION), orden, filtro, 1).status_code == 409


def test_el_precio_se_copia_al_registrar_la_linea(db, abrir_orden, como, filtro):
    """RN-05: subir el precio del catálogo no cambia las órdenes ya registradas."""
    orden = abrir_orden()
    agregar_repuesto(como(RECEPCION), orden, filtro, 1)

    como(ADMIN).patch(f"/api/v1/repuestos/{filtro.id}", json={"precio_venta": "30000"})
    detalle = como(ADMIN).get(f"/api/v1/ordenes/{orden['id']}").json()

    assert Decimal(detalle["repuestos"][0]["precio_unitario"]) == 25000
    assert Decimal(detalle["liquidacion"]["repuestos"]) == 25000


def test_quitar_repuesto_lo_devuelve_al_stock(db, abrir_orden, como, filtro):
    orden = abrir_orden()
    linea = agregar_repuesto(como(MECANICO), orden, filtro, 3).json()["repuestos"][0]

    respuesta = borrar(como(MECANICO), f"/api/v1/ordenes/{orden['id']}/repuestos/{linea['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["repuestos"] == []
    assert stock(db, filtro) == 10
    tipos = [(m.tipo, m.cantidad) for m in movimientos(db, filtro)]
    assert tipos == [(TipoMovimiento.SALIDA, -3), (TipoMovimiento.DEVOLUCION, 3)]


def test_cancelar_la_orden_devuelve_todos_los_repuestos(db, abrir_orden, como, filtro, aceite):
    """RN-03. Las líneas se conservan como historia; el stock vuelve con DEVOLUCION."""
    orden = abrir_orden()
    agregar_repuesto(como(RECEPCION), orden, filtro, 2)
    agregar_repuesto(como(RECEPCION), orden, aceite, "4.5")

    respuesta = cambiar(como(RECEPCION), orden, "CANCELADA", "El cliente no aprobó")

    assert respuesta.status_code == 201, respuesta.text
    assert stock(db, filtro) == 10
    assert stock(db, aceite) == 8
    assert movimientos(db, aceite)[-1].tipo == TipoMovimiento.DEVOLUCION
    assert len(respuesta.json()["repuestos"]) == 2


def test_entregar_no_devuelve_stock(db, abrir_orden, como, filtro):
    orden = abrir_orden()
    agregar_repuesto(como(MECANICO), orden, filtro, 2)
    cliente = como(MECANICO)
    cambiar(cliente, orden, "EN_DIAGNOSTICO")
    cliente.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Cambio de filtro"})
    cambiar(cliente, orden, "REPARADO")

    assert cambiar(como(RECEPCION), orden, "ENTREGADO").status_code == 201
    assert stock(db, filtro) == 8


def test_orden_cerrada_no_admite_lineas(abrir_orden, como, filtro):
    """RN-07."""
    orden = abrir_orden()
    linea = agregar_repuesto(como(RECEPCION), orden, filtro, 1).json()["repuestos"][0]
    cambiar(como(RECEPCION), orden, "CANCELADA", "Error de registro")
    cliente = como(ADMIN)

    assert agregar_repuesto(cliente, orden, filtro, 1).status_code == 409
    assert agregar_servicio(cliente, orden).status_code == 409
    quitar = borrar(cliente, f"/api/v1/ordenes/{orden['id']}/repuestos/{linea['id']}")
    assert quitar.status_code == 409


def test_repuesto_inactivo_no_se_puede_agregar(abrir_orden, como, taller_a, crear_repuesto):
    inactivo = crear_repuesto(taller_a, "VIEJO", activo=False)
    respuesta = agregar_repuesto(como(RECEPCION), abrir_orden(), inactivo, 1)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "repuesto_id"


@pytest.mark.parametrize("cantidad", ["0", "-1", "1.234", "abc"])
def test_cantidad_invalida(abrir_orden, como, filtro, cantidad):
    respuesta = agregar_repuesto(como(RECEPCION), abrir_orden(), filtro, cantidad)
    assert respuesta.status_code == 422


# --- Mano de obra -----------------------------------------------------------------------------


def test_agregar_y_quitar_mano_de_obra(abrir_orden, como, equipo):
    orden = abrir_orden()
    cliente = como(MECANICO)

    respuesta = agregar_servicio(cliente, orden, "Revisión de suspensión", "60000")
    assert respuesta.status_code == 201
    [linea] = respuesta.json()["servicios"]
    assert linea["descripcion"] == "Revisión de suspensión"
    assert Decimal(linea["subtotal"]) == 60000
    assert linea["registrador"]["id"] == equipo["mecanico"].id

    sin_linea = borrar(cliente, f"/api/v1/ordenes/{orden['id']}/servicios/{linea['id']}")
    assert sin_linea.json()["servicios"] == []


@pytest.mark.parametrize(
    ("cuerpo", "campo"),
    [
        ({"descripcion": "", "precio_unitario": "1000"}, "descripcion"),
        ({"descripcion": "Alineación"}, "precio_unitario"),
        ({"descripcion": "Alineación", "precio_unitario": "-5"}, "precio_unitario"),
    ],
)
def test_mano_de_obra_invalida(abrir_orden, como, cuerpo, campo):
    orden = abrir_orden()
    respuesta = como(RECEPCION).post(f"/api/v1/ordenes/{orden['id']}/servicios", json=cuerpo)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == campo


def test_linea_de_otra_orden_responde_404(abrir_orden, como, crear_vehiculo, ana, filtro):
    primera = abrir_orden()
    segunda = abrir_orden(vehiculo=crear_vehiculo(ana, "DEF456"))
    linea = agregar_servicio(como(RECEPCION), primera).json()["servicios"][0]

    respuesta = borrar(como(RECEPCION), f"/api/v1/ordenes/{segunda['id']}/servicios/{linea['id']}")

    assert respuesta.status_code == 404


# --- Liquidación (RF-12, RN-06) -----------------------------------------------------------------


def test_liquidacion_suma_mano_de_obra_y_repuestos_con_decimales_exactos(
    abrir_orden, como, filtro, aceite
):
    orden = abrir_orden()
    cliente = como(RECEPCION)
    agregar_servicio(cliente, orden, "Cambio de aceite", "40000")
    agregar_servicio(cliente, orden, "Lavado de motor", "15000.50", cantidad="2")
    agregar_repuesto(cliente, orden, filtro, 1)
    detalle = agregar_repuesto(cliente, orden, aceite, "1.5").json()

    # 1,5 L × $32.333 = $48.499,50: sin errores de coma flotante.
    assert Decimal(detalle["repuestos"][1]["subtotal"]) == Decimal("48499.50")
    assert detalle["liquidacion"] == {
        "mano_de_obra": "70001.00",
        "repuestos": "73499.50",
        "total": "143500.50",
    }


def test_orden_sin_lineas_liquida_en_cero(abrir_orden):
    assert abrir_orden()["liquidacion"] == {
        "mano_de_obra": "0.00",
        "repuestos": "0.00",
        "total": "0.00",
    }


def test_el_total_no_se_puede_enviar_desde_el_cliente(abrir_orden, como):
    orden = abrir_orden()
    como(RECEPCION).patch(f"/api/v1/ordenes/{orden['id']}", json={"liquidacion": {"total": "1"}})
    detalle = como(RECEPCION).get(f"/api/v1/ordenes/{orden['id']}").json()
    assert detalle["liquidacion"]["total"] == "0.00"


# --- Roles y aislamiento ------------------------------------------------------------------------


def test_mecanico_no_asignado_no_ve_la_orden(abrir_orden, como, filtro):
    """S3-5: el mecánico solo ve sus órdenes; las demás no existen para él."""
    orden = abrir_orden()
    cliente = como(OTRO_MECANICO)
    assert agregar_repuesto(cliente, orden, filtro, 1).status_code == 404
    assert agregar_servicio(cliente, orden).status_code == 404


def test_repuesto_de_otro_taller_responde_404(db, abrir_orden, como, taller_b, crear_repuesto):
    ajeno = crear_repuesto(taller_b, "W712")

    respuesta = agregar_repuesto(como(RECEPCION), abrir_orden(), ajeno, 1)

    assert respuesta.status_code == 404
    assert codigo_error(respuesta) == "NO_ENCONTRADO"
    assert stock(db, ajeno) == 10


def test_orden_de_otro_taller_responde_404(
    abrir_orden, como, taller_b, crear_usuario, crear_repuesto
):
    orden = abrir_orden()
    crear_usuario(taller_b, "admin@b.co")
    propio = crear_repuesto(taller_b, "W712")

    respuesta = agregar_repuesto(como("admin@b.co"), orden, propio, 1)

    assert respuesta.status_code == 404
