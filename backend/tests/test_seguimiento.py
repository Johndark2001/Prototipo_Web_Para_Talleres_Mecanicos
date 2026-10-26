"""Seguimiento público por enlace (RF-13, ADR-005): sin sesión y sin datos personales."""

import json

import pytest

from tests.conftest import RECEPCION, cambiar


@pytest.fixture
def orden_con_lineas(abrir_orden, como, taller_a, crear_repuesto):
    filtro = crear_repuesto(taller_a, "W712", precio_venta="25000")
    orden = abrir_orden(kilometraje=48900)
    cliente = como(RECEPCION)
    cliente.post(
        f"/api/v1/ordenes/{orden['id']}/servicios",
        json={"descripcion": "Cambio de filtro", "precio_unitario": "20000"},
    )
    cliente.post(
        f"/api/v1/ordenes/{orden['id']}/repuestos",
        json={"repuesto_id": filtro.id, "cantidad": "1"},
    )
    cliente.post("/api/v1/auth/logout", json={})
    return orden


def ver(cliente, codigo):
    return cliente.get(f"/api/v1/seguimiento/{codigo}")


def test_el_cliente_ve_su_orden_sin_iniciar_sesion(cliente, orden_con_lineas):
    respuesta = ver(cliente, orden_con_lineas["codigo_seguimiento"])

    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert datos["taller"] == "Taller A"
    assert datos["numero"] == orden_con_lineas["numero"]
    assert datos["placa"] == "ABC***"
    assert (datos["marca"], datos["modelo"]) == ("Mazda", "3")
    assert datos["estado"] == "RECIBIDO"
    assert [e["estado"] for e in datos["etapas"]] == ["RECIBIDO"]
    assert datos["servicios"][0]["descripcion"] == "Cambio de filtro"
    assert datos["repuestos"][0]["nombre"] == "Filtro de aceite"
    assert datos["liquidacion"]["total"] == "45000.00"


def test_no_expone_datos_personales_ni_internos(cliente, orden_con_lineas, ana, equipo):
    texto = json.dumps(ver(cliente, orden_con_lineas["codigo_seguimiento"]).json())

    prohibidos = [
        ana.nombre,
        ana.telefono,
        "ABC123",  # placa completa
        "Ruido en la suspensión",  # motivo de ingreso: nota interna del taller
        equipo["mecanico"].nombre,
        equipo["recepcion"].nombre,
        "48900",  # kilometraje
    ]
    for dato in prohibidos:
        assert dato not in texto, dato
    assert set(json.loads(texto)) == {
        "taller",
        "numero",
        "placa",
        "marca",
        "modelo",
        "estado",
        "etapas",
        "servicios",
        "repuestos",
        "liquidacion",
    }


def test_las_etapas_no_incluyen_notas_ni_usuarios(cliente, abrir_orden, como):
    orden = abrir_orden()
    cambiar(como(RECEPCION), orden, "CANCELADA", "Cliente moroso, no volver a recibir")
    cliente.post("/api/v1/auth/logout", json={})

    datos = ver(cliente, orden["codigo_seguimiento"]).json()

    assert datos["estado"] == "CANCELADA"
    assert all(set(etapa) == {"estado", "fecha"} for etapa in datos["etapas"])
    assert "moroso" not in json.dumps(datos)


@pytest.mark.parametrize(
    "codigo", ["noexiste-pero-tiene-formato", "corto", "con espacios y ñ", "a" * 100]
)
def test_codigo_desconocido_o_mal_formado_responde_404(cliente, orden_con_lineas, codigo):
    respuesta = ver(cliente, codigo)
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "NO_ENCONTRADO"


def test_demasiadas_consultas_seguidas_responden_429(cliente, orden_con_lineas):
    codigo = orden_con_lineas["codigo_seguimiento"]
    respuestas = [ver(cliente, codigo).status_code for _ in range(31)]
    assert respuestas[:30] == [200] * 30
    assert respuestas[30] == 429
