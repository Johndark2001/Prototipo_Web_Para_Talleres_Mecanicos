"""Cambio #6: el cliente y su primer vehículo se registran en una sola operación."""

from sqlalchemy import func, select

from app.models import Cliente, Vehiculo
from tests.conftest import ADMIN, MECANICO, RECEPCION

CLIENTE = {"nombre": "Luis Pérez", "telefono": "300 555 1234", "autoriza_datos": True}
MOTO = {"tipo": "MOTO", "placa": "abc-12d", "marca": "Yamaha", "modelo": "FZ", "anio": 2022}


def contar(db, modelo) -> int:
    db.expire_all()
    return db.scalar(select(func.count()).select_from(modelo))


def test_recepcion_crea_cliente_y_vehiculo_juntos(como, equipo, db):
    respuesta = como(RECEPCION).post("/api/v1/clientes", json={**CLIENTE, "vehiculo": MOTO})

    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()
    assert datos["nombre"] == "Luis Pérez"
    assert [(v["placa"], v["tipo"]) for v in datos["vehiculos"]] == [("ABC12D", "MOTO")]
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "ABC12D"))
    assert vehiculo.cliente_id == datos["id"]


def test_sin_vehiculo_sigue_funcionando(como, equipo):
    respuesta = como(ADMIN).post("/api/v1/clientes", json=CLIENTE)
    assert respuesta.status_code == 201
    assert respuesta.json()["vehiculos"] == []


def test_si_la_placa_existe_no_se_guarda_nada(como, equipo, carro, db):
    clientes_antes = contar(db, Cliente)
    respuesta = como(RECEPCION).post(
        "/api/v1/clientes",
        json={**CLIENTE, "vehiculo": {**MOTO, "placa": "ABC123"}},
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "vehiculo.placa"
    assert contar(db, Cliente) == clientes_antes
    assert contar(db, Vehiculo) == 1


def test_un_vehiculo_invalido_se_reporta_con_su_campo(como, equipo, db):
    respuesta = como(RECEPCION).post(
        "/api/v1/clientes", json={**CLIENTE, "vehiculo": {**MOTO, "marca": ""}}
    )

    assert respuesta.status_code == 422
    campos = [d["campo"] for d in respuesta.json()["error"]["details"]]
    assert campos == ["vehiculo.marca"]
    assert contar(db, Cliente) == 0


def test_el_mecanico_no_registra_clientes_con_vehiculo(como, equipo):
    respuesta = como(MECANICO).post("/api/v1/clientes", json={**CLIENTE, "vehiculo": MOTO})
    assert respuesta.status_code == 403


def test_desde_la_ficha_del_cliente_se_agregan_mas_vehiculos(como, equipo):
    cliente_http = como(RECEPCION)
    luis = cliente_http.post("/api/v1/clientes", json={**CLIENTE, "vehiculo": MOTO}).json()
    respuesta = cliente_http.post(
        "/api/v1/vehiculos",
        json={"placa": "MZD333", "marca": "Mazda", "modelo": "3", "cliente_id": luis["id"]},
    )

    assert respuesta.status_code == 201
    ficha = cliente_http.get(f"/api/v1/clientes/{luis['id']}").json()
    assert sorted(v["placa"] for v in ficha["vehiculos"]) == ["ABC12D", "MZD333"]
