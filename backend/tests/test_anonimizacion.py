"""Anonimización del cliente (RN-11, RNF-06): se borran sus datos personales, no su historia."""

import json

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import Cliente
from tests.conftest import ADMIN, MECANICO, RECEPCION, cambiar, codigo_error

CONFIRMAR = {"confirmacion": "ANONIMIZAR"}


@pytest.fixture
def ana_completa(taller_a, crear_cliente):
    return crear_cliente(
        taller_a, "Ana Gómez", telefono="3001234567", email="ana@correo.co", documento="1144000111"
    )


@pytest.fixture
def orden_entregada(abrir_orden, como, ana_completa, crear_vehiculo):
    carro = crear_vehiculo(ana_completa, "DEF456")
    orden = abrir_orden(vehiculo=carro)
    mecanico = como(MECANICO)
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Cambio de rótula"})
    for estado in ("EN_DIAGNOSTICO", "REPARADO"):
        assert cambiar(mecanico, orden, estado).status_code == 201
    assert cambiar(como(RECEPCION), orden, "ENTREGADO").status_code == 201
    return orden


def anonimizar(cliente_http, cliente_id, cuerpo=CONFIRMAR):
    return cliente_http.post(f"/api/v1/clientes/{cliente_id}/anonimizar", json=cuerpo)


def test_admin_anonimiza_los_datos_personales_y_queda_la_auditoria(como, equipo, ana_completa, db):
    respuesta = anonimizar(como(ADMIN), ana_completa.id)

    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert datos["nombre"] == f"Cliente anonimizado N.º {ana_completa.id}"
    assert datos["telefono"] == ""
    assert datos["email"] is None
    assert datos["documento"] is None
    assert datos["anonimizado"] is True
    assert datos["activo"] is False
    assert datos["anonimizado_en"] is not None
    assert datos["anonimizador"] == {"id": equipo["admin"].id, "nombre": equipo["admin"].nombre}
    # La autorización se conserva como prueba de que el dato se trató con permiso (RN-10).
    assert datos["autoriza_datos"] is True

    db.expire_all()
    guardado = db.get(Cliente, ana_completa.id)
    assert guardado.anonimizado_por == equipo["admin"].id
    texto = json.dumps([guardado.nombre, guardado.telefono, guardado.email, guardado.documento])
    for dato in ("Ana", "Gómez", "3001234567", "ana@correo.co", "1144000111"):
        assert dato not in texto


def test_se_conservan_las_ordenes_los_carros_y_el_historial(como, orden_entregada, ana_completa):
    admin = como(ADMIN)
    assert anonimizar(admin, ana_completa.id).status_code == 200

    detalle = admin.get(f"/api/v1/ordenes/{orden_entregada['id']}").json()
    assert detalle["estado"] == "ENTREGADO"
    assert detalle["cliente"]["id"] == ana_completa.id
    assert detalle["cliente"]["nombre"] == f"Cliente anonimizado N.º {ana_completa.id}"
    assert [h["estado_nuevo"] for h in detalle["historial"]] == [
        "RECIBIDO",
        "EN_DIAGNOSTICO",
        "REPARADO",
        "ENTREGADO",
    ]

    cliente = admin.get(f"/api/v1/clientes/{ana_completa.id}").json()
    assert [v["placa"] for v in cliente["vehiculos"]] == ["DEF456"]
    vehiculo_id = cliente["vehiculos"][0]["id"]
    historial = admin.get("/api/v1/ordenes", params={"vehiculo_id": vehiculo_id}).json()
    assert [o["id"] for o in historial["data"]] == [orden_entregada["id"]]


def test_el_seguimiento_publico_sigue_funcionando(cliente, como, orden_entregada, ana_completa):
    assert anonimizar(como(ADMIN), ana_completa.id).status_code == 200
    cliente.post("/api/v1/auth/logout", json={})

    respuesta = cliente.get(f"/api/v1/seguimiento/{orden_entregada['codigo_seguimiento']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ENTREGADO"
    assert respuesta.json()["placa"] == "DEF***"


@pytest.mark.parametrize("correo", [RECEPCION, MECANICO])
def test_solo_el_admin_puede_anonimizar(como, equipo, ana_completa, db, correo):
    respuesta = anonimizar(como(correo), ana_completa.id)

    assert respuesta.status_code == 403
    db.expire_all()
    assert db.get(Cliente, ana_completa.id).nombre == "Ana Gómez"


def test_sin_sesion_responde_401(cliente, ana_completa):
    assert anonimizar(cliente, ana_completa.id).status_code == 401


@pytest.mark.parametrize("cuerpo", [{}, {"confirmacion": "si"}, {"confirmacion": True}])
def test_exige_la_confirmacion_escrita(como, equipo, ana_completa, db, cuerpo):
    respuesta = anonimizar(como(ADMIN), ana_completa.id, cuerpo)

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "confirmacion"
    db.expire_all()
    assert db.get(Cliente, ana_completa.id).anonimizado is False


def test_no_se_anonimiza_con_ordenes_abiertas(como, abrir_orden, ana_completa, crear_vehiculo, db):
    abrir_orden(vehiculo=crear_vehiculo(ana_completa, "XYZ987"))

    respuesta = anonimizar(como(ADMIN), ana_completa.id)

    assert respuesta.status_code == 409
    assert "órdenes abiertas" in respuesta.json()["error"]["message"]
    db.expire_all()
    assert db.get(Cliente, ana_completa.id).anonimizado is False


def test_una_orden_cancelada_no_impide_anonimizar(como, abrir_orden, ana_completa, crear_vehiculo):
    orden = abrir_orden(vehiculo=crear_vehiculo(ana_completa, "XYZ987"))
    assert cambiar(como(RECEPCION), orden, "CANCELADA", "El cliente desistió").status_code == 201

    assert anonimizar(como(ADMIN), ana_completa.id).status_code == 200


def test_no_se_anonimiza_dos_veces(como, equipo, ana_completa):
    admin = como(ADMIN)
    primera = anonimizar(admin, ana_completa.id).json()

    respuesta = anonimizar(admin, ana_completa.id)

    assert respuesta.status_code == 409
    # La auditoría original no se reemplaza.
    assert (
        admin.get(f"/api/v1/clientes/{ana_completa.id}").json()["anonimizado_en"]
        == (primera["anonimizado_en"])
    )


@pytest.mark.parametrize(
    "cambio", [{"activo": True}, {"nombre": "Ana Gómez"}, {"telefono": "3001234567"}]
)
def test_un_cliente_anonimizado_no_se_edita_ni_se_reactiva(como, equipo, ana_completa, cambio):
    assert anonimizar(como(ADMIN), ana_completa.id).status_code == 200

    respuesta = como(RECEPCION).patch(f"/api/v1/clientes/{ana_completa.id}", json=cambio)

    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CONFLICTO"


def test_el_documento_queda_libre_para_un_registro_nuevo(como, equipo, ana_completa):
    # Si la persona vuelve al taller, se registra de nuevo con su autorización (RN-10).
    assert anonimizar(como(ADMIN), ana_completa.id).status_code == 200

    respuesta = como(RECEPCION).post(
        "/api/v1/clientes",
        json={
            "nombre": "Ana Gómez",
            "telefono": "3001234567",
            "documento": "1144000111",
            "autoriza_datos": True,
        },
    )

    assert respuesta.status_code == 201


def test_aislamiento_cliente_de_otro_taller(como, equipo, taller_b, crear_cliente, db):
    ajeno = crear_cliente(taller_b, "Luis Pérez")

    respuesta = anonimizar(como(ADMIN), ajeno.id)

    assert respuesta.status_code == 404
    db.expire_all()
    assert db.get(Cliente, ajeno.id).anonimizado is False


def test_cliente_sin_anonimizar_no_tiene_auditoria(como, equipo, ana_completa):
    datos = como(ADMIN).get(f"/api/v1/clientes/{ana_completa.id}").json()
    assert datos["anonimizado"] is False
    assert datos["anonimizado_en"] is None
    assert datos["anonimizador"] is None


def test_la_base_rechaza_una_anonimizacion_sin_auditoria(db, ana_completa):
    # Segunda barrera: aunque falle el servicio, no queda un anonimizado sin quién ni cuándo.
    with pytest.raises(IntegrityError, match="ck_cliente_anonimizacion_coherente"):
        db.execute(
            text("UPDATE cliente SET anonimizado = true, activo = false WHERE id = :id"),
            {"id": ana_completa.id},
        )
    db.rollback()


def test_la_base_rechaza_un_anonimizado_que_conserva_el_documento(db, equipo, ana_completa):
    with pytest.raises(IntegrityError, match="ck_cliente_anonimizacion_coherente"):
        db.execute(
            text(
                "UPDATE cliente SET anonimizado = true, activo = false, email = NULL,"
                " anonimizado_en = now(), anonimizado_por = :u WHERE id = :id"
            ),
            {"id": ana_completa.id, "u": equipo["admin"].id},
        )
    db.rollback()
