"""Inventario (RF-08, RF-10): catálogo, entradas, ajustes, movimientos, roles y aislamiento."""

from decimal import Decimal

import pytest

from app.models import MovimientoInventario
from tests.conftest import ADMIN, MECANICO, RECEPCION, codigo_error

FILTRO = {
    "codigo": " w712 ",
    "nombre": "Filtro de aceite Mann",
    "unidad": "unidad",
    "precio_venta": "25000",
    "stock_minimo": "3",
    "stock_inicial": "10",
}


def crear(cliente, **cambios):
    return cliente.post("/api/v1/repuestos", json={**FILTRO, **cambios})


def mover(cliente, repuesto_id, **cuerpo):
    return cliente.post(f"/api/v1/repuestos/{repuesto_id}/movimientos", json=cuerpo)


def movimientos(cliente, repuesto_id) -> list[dict]:
    return cliente.get(f"/api/v1/repuestos/{repuesto_id}/movimientos").json()["data"]


# --- Catálogo ------------------------------------------------------------------------------


def test_admin_crea_repuesto_y_el_stock_inicial_queda_como_entrada(como, equipo):
    cliente = como(ADMIN)

    respuesta = crear(cliente)

    assert respuesta.status_code == 201, respuesta.text
    repuesto = respuesta.json()
    assert repuesto["codigo"] == "W712"  # se normaliza a mayúsculas sin espacios
    assert Decimal(repuesto["stock_actual"]) == 10
    assert Decimal(repuesto["precio_venta"]) == 25000
    assert repuesto["stock_bajo"] is False
    [entrada] = movimientos(cliente, repuesto["id"])
    assert entrada["tipo"] == "ENTRADA"
    assert Decimal(entrada["cantidad"]) == 10
    assert Decimal(entrada["stock_resultante"]) == 10
    assert entrada["usuario"]["id"] == equipo["admin"].id


def test_repuesto_sin_stock_inicial_no_genera_movimiento(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente, stock_inicial="0").json()
    assert movimientos(cliente, repuesto["id"]) == []


def test_codigo_repetido_en_el_taller_responde_422(como, equipo):
    cliente = como(ADMIN)
    crear(cliente)

    respuesta = crear(cliente, codigo="W712", nombre="Otro filtro")

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "codigo"


def test_otro_taller_puede_usar_el_mismo_codigo(como, equipo, taller_b, crear_usuario):
    crear(como(ADMIN))
    crear_usuario(taller_b, "admin@b.co")
    assert crear(como("admin@b.co")).status_code == 201


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("precio_venta", "-1"), ("stock_inicial", "-5"), ("precio_venta", "12.345"), ("codigo", "")],
)
def test_datos_invalidos_del_repuesto(como, equipo, campo, valor):
    respuesta = crear(como(ADMIN), **{campo: valor})
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == campo


@pytest.mark.parametrize("email", [RECEPCION, MECANICO])
def test_solo_el_admin_modifica_el_inventario_pero_todos_lo_consultan(
    como, equipo, crear_repuesto, taller_a, email
):
    repuesto = crear_repuesto(taller_a)
    cliente = como(email)

    assert crear(cliente).status_code == 403
    assert (
        cliente.patch(
            f"/api/v1/repuestos/{repuesto.id}", json={"nombre": "Otro nombre"}
        ).status_code
        == 403
    )
    assert mover(cliente, repuesto.id, tipo="ENTRADA", cantidad="1").status_code == 403
    assert cliente.get(f"/api/v1/repuestos/{repuesto.id}/movimientos").status_code == 403
    listado = cliente.get("/api/v1/repuestos")
    assert listado.status_code == 200
    assert [r["codigo"] for r in listado.json()["data"]] == ["W712"]


def test_editar_precio_y_minimo_no_toca_el_stock(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()

    respuesta = cliente.patch(
        f"/api/v1/repuestos/{repuesto['id']}",
        json={"precio_venta": "27000", "stock_minimo": "12", "stock_actual": "999"},
    )

    assert respuesta.status_code == 200
    editado = respuesta.json()
    assert Decimal(editado["precio_venta"]) == 27000
    assert Decimal(editado["stock_actual"]) == 10  # el stock solo cambia con movimientos
    assert editado["stock_bajo"] is True  # 10 <= 12 (RN-04)


# --- Entradas y ajustes ----------------------------------------------------------------------


def test_entrada_suma_al_stock(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()

    respuesta = mover(cliente, repuesto["id"], tipo="ENTRADA", cantidad="5", nota="Factura 123")

    assert respuesta.status_code == 201
    assert Decimal(respuesta.json()["stock_actual"]) == 15
    ultimo = movimientos(cliente, repuesto["id"])[0]
    assert (ultimo["tipo"], Decimal(ultimo["cantidad"]), ultimo["nota"]) == (
        "ENTRADA",
        5,
        "Factura 123",
    )


def test_entrada_admite_decimales_con_dos_cifras(como, equipo):
    cliente = como(ADMIN)
    aceite = crear(cliente, codigo="ACE20W50", unidad="litro", stock_inicial="0").json()

    assert mover(cliente, aceite["id"], tipo="ENTRADA", cantidad="4.5").status_code == 201
    assert mover(cliente, aceite["id"], tipo="ENTRADA", cantidad="0.333").status_code == 422


def test_entrada_sin_cantidad_o_negativa_es_rechazada(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()

    sin_cantidad = mover(cliente, repuesto["id"], tipo="ENTRADA")
    negativa = mover(cliente, repuesto["id"], tipo="ENTRADA", cantidad="-2")

    assert sin_cantidad.status_code == negativa.status_code == 422
    assert sin_cantidad.json()["error"]["details"][0]["campo"] == "cantidad"


def test_ajuste_deja_el_stock_en_lo_contado_y_registra_la_diferencia(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()

    respuesta = mover(
        cliente, repuesto["id"], tipo="AJUSTE", stock_contado="7", nota="Conteo de fin de mes"
    )

    assert respuesta.status_code == 201
    assert Decimal(respuesta.json()["stock_actual"]) == 7
    ajuste = movimientos(cliente, repuesto["id"])[0]
    assert ajuste["tipo"] == "AJUSTE"
    assert Decimal(ajuste["cantidad"]) == -3
    assert Decimal(ajuste["stock_resultante"]) == 7


@pytest.mark.parametrize(
    ("cuerpo", "campo"),
    [
        ({"stock_contado": "7"}, "nota"),
        ({"nota": "Conteo"}, "stock_contado"),
        ({"stock_contado": "10", "nota": "Conteo"}, "stock_contado"),  # no cambia nada
        ({"stock_contado": "-1", "nota": "Conteo"}, "stock_contado"),
    ],
)
def test_ajuste_invalido(como, equipo, cuerpo, campo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()

    respuesta = mover(cliente, repuesto["id"], tipo="AJUSTE", **cuerpo)

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == campo


def test_no_se_registran_salidas_ni_devoluciones_a_mano(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()
    for tipo in ("SALIDA", "DEVOLUCION"):
        assert mover(cliente, repuesto["id"], tipo=tipo, cantidad="1").status_code == 422


def test_repuesto_inactivo_no_admite_movimientos(como, equipo):
    cliente = como(ADMIN)
    repuesto = crear(cliente).json()
    cliente.patch(f"/api/v1/repuestos/{repuesto['id']}", json={"activo": False})

    respuesta = mover(cliente, repuesto["id"], tipo="ENTRADA", cantidad="1")

    assert respuesta.status_code == 409


def test_la_base_impide_un_stock_negativo(db, taller_a, crear_repuesto):
    """RN-02: aunque el código fallara, la restricción CHECK de la base lo rechaza."""
    from sqlalchemy.exc import IntegrityError

    repuesto = crear_repuesto(taller_a, stock_actual="1")
    repuesto.stock_actual = Decimal("-1")
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


# --- Alertas y filtros -----------------------------------------------------------------------


def test_filtro_stock_bajo_y_busqueda(como, equipo, crear_repuesto, taller_a):
    crear_repuesto(taller_a, "W712", nombre="Filtro de aceite", stock_actual="2", stock_minimo="3")
    crear_repuesto(taller_a, "B330", nombre="Buje de tijera", stock_actual="5", stock_minimo="2")
    crear_repuesto(
        taller_a, "PAS01", nombre="Pastillas de freno", stock_actual="0", stock_minimo="0"
    )
    cliente = como(RECEPCION)

    bajos = cliente.get("/api/v1/repuestos", params={"stock_bajo": True}).json()["data"]
    por_nombre = cliente.get("/api/v1/repuestos", params={"buscar": "tijera"}).json()["data"]
    por_codigo = cliente.get("/api/v1/repuestos", params={"buscar": "w71"}).json()["data"]

    # Agotado cuenta como alerta aunque el mínimo sea cero (RN-04: "igual o por debajo").
    assert {r["codigo"] for r in bajos} == {"W712", "PAS01"}
    assert [r["codigo"] for r in por_nombre] == ["B330"]
    assert [r["codigo"] for r in por_codigo] == ["W712"]


# --- Aislamiento entre talleres (ADR-006) ----------------------------------------------------


def test_admin_de_otro_taller_no_ve_ni_mueve_repuestos_ajenos(
    como, equipo, crear_repuesto, taller_a, taller_b, crear_usuario
):
    ajeno = crear_repuesto(taller_a)
    crear_usuario(taller_b, "admin@b.co")
    cliente = como("admin@b.co")

    assert cliente.get("/api/v1/repuestos").json()["data"] == []
    assert cliente.get(f"/api/v1/repuestos/{ajeno.id}").status_code == 404
    assert (
        cliente.patch(f"/api/v1/repuestos/{ajeno.id}", json={"nombre": "Otro nombre"}).status_code
        == 404
    )
    assert mover(cliente, ajeno.id, tipo="ENTRADA", cantidad="1").status_code == 404
    assert cliente.get(f"/api/v1/repuestos/{ajeno.id}/movimientos").status_code == 404


def test_el_taller_sale_de_la_sesion_al_crear(como, equipo, taller_b, db):
    respuesta = crear(como(ADMIN), taller_id=taller_b.id)
    assert respuesta.status_code == 201
    movimiento = db.query(MovimientoInventario).one()
    assert movimiento.usuario_id == equipo["admin"].id


def test_repuesto_inexistente_usa_el_formato_de_error_comun(como, equipo):
    respuesta = como(ADMIN).get("/api/v1/repuestos/999")
    assert respuesta.status_code == 404
    assert codigo_error(respuesta) == "NO_ENCONTRADO"
