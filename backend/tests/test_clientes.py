import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import RolUsuario
from tests.conftest import iniciar_sesion

NUEVO_CLIENTE = {
    "nombre": "Ana Gómez",
    "telefono": "300 123 4567",
    "email": "Ana@Correo.co",
    "documento": "1.144.000.111",
    "autoriza_datos": True,
}


@pytest.fixture
def recepcion_a(cliente, taller_a, crear_usuario):
    usuario = crear_usuario(taller_a, "recepcion@a.co", rol=RolUsuario.RECEPCION)
    iniciar_sesion(cliente, "recepcion@a.co")
    return usuario


def campos_con_error(respuesta) -> set[str]:
    return {detalle["campo"] for detalle in respuesta.json()["error"]["details"]}


def test_crea_cliente_con_autorizacion_y_datos_normalizados(cliente, recepcion_a):
    respuesta = cliente.post("/api/v1/clientes", json=NUEVO_CLIENTE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["telefono"] == "3001234567"
    assert cuerpo["email"] == "ana@correo.co"
    assert cuerpo["documento"] == "1144000111"
    assert cuerpo["autoriza_datos"] is True
    assert cuerpo["fecha_autorizacion"] is not None


@pytest.mark.parametrize("autoriza", [False, None])
def test_no_se_registra_cliente_sin_autorizacion(cliente, recepcion_a, autoriza):
    # RN-10 / Ley 1581: ni falsa ni ausente.
    datos = {**NUEVO_CLIENTE, "autoriza_datos": autoriza}
    if autoriza is None:
        del datos["autoriza_datos"]

    respuesta = cliente.post("/api/v1/clientes", json=datos)

    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {"autoriza_datos"}
    assert cliente.get("/api/v1/clientes").json()["pagination"]["total_items"] == 0


def test_la_base_rechaza_un_cliente_sin_autorizacion(db, taller_a):
    # Segunda barrera de RN-10: aunque falle la API, la restricción CHECK lo impide.
    with pytest.raises(IntegrityError, match="ck_cliente_autoriza_datos_obligatoria"):
        db.execute(
            text(
                "INSERT INTO cliente (taller_id, nombre, telefono, autoriza_datos,"
                " fecha_autorizacion) VALUES (:t, 'X', '3000000000', false, now())"
            ),
            {"t": taller_a.id},
        )
    db.rollback()


def test_campos_opcionales_en_blanco_se_guardan_vacios(cliente, recepcion_a):
    datos = {**NUEVO_CLIENTE, "email": "", "documento": "  "}
    cuerpo = cliente.post("/api/v1/clientes", json=datos).json()
    assert cuerpo["email"] is None
    assert cuerpo["documento"] is None


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("telefono", "12"), ("telefono", "300-abc"), ("email", "no-es-correo"), ("nombre", "A")],
)
def test_datos_invalidos_responden_422_con_el_campo(cliente, recepcion_a, campo, valor):
    respuesta = cliente.post("/api/v1/clientes", json={**NUEVO_CLIENTE, campo: valor})
    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {campo}


def test_documento_repetido_en_el_taller_responde_422(cliente, recepcion_a):
    cliente.post("/api/v1/clientes", json=NUEVO_CLIENTE)
    respuesta = cliente.post("/api/v1/clientes", json={**NUEVO_CLIENTE, "documento": "1144000111"})
    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {"documento"}


def test_mismo_documento_se_permite_en_otro_taller(cliente, recepcion_a, taller_b, crear_cliente):
    crear_cliente(taller_b, documento="1144000111")
    assert cliente.post("/api/v1/clientes", json=NUEVO_CLIENTE).status_code == 201


def test_busqueda_por_nombre_telefono_o_documento(cliente, recepcion_a, taller_a, crear_cliente):
    crear_cliente(taller_a, "Ana Gómez", telefono="3001112233", documento="111")
    crear_cliente(taller_a, "Pedro Ruiz", telefono="3159998877")

    def nombres(q):
        datos = cliente.get("/api/v1/clientes", params={"q": q}).json()["data"]
        return {c["nombre"] for c in datos}

    assert nombres("gómez") == {"Ana Gómez"}
    assert nombres("315 999") == {"Pedro Ruiz"}
    assert nombres("111") == {"Ana Gómez"}
    assert nombres("100%") == set()  # los comodines de LIKE se tratan como texto


def test_listado_cuenta_solo_los_carros_activos(
    cliente, recepcion_a, taller_a, crear_cliente, crear_vehiculo
):
    ana = crear_cliente(taller_a)
    crear_vehiculo(ana, "ABC123")
    crear_vehiculo(ana, "XYZ987", activo=False)

    fila = cliente.get("/api/v1/clientes").json()["data"][0]

    assert fila["total_vehiculos"] == 1


def test_detalle_incluye_los_carros_del_cliente(
    cliente, recepcion_a, taller_a, crear_cliente, crear_vehiculo
):
    ana = crear_cliente(taller_a)
    crear_vehiculo(ana, "ABC123")

    cuerpo = cliente.get(f"/api/v1/clientes/{ana.id}").json()

    assert [v["placa"] for v in cuerpo["vehiculos"]] == ["ABC123"]


def test_editar_y_desactivar_cliente(cliente, recepcion_a, taller_a, crear_cliente):
    ana = crear_cliente(taller_a, email="ana@a.co")

    respuesta = cliente.patch(
        f"/api/v1/clientes/{ana.id}", json={"telefono": "315 000 1111", "email": ""}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["telefono"] == "3150001111"
    assert respuesta.json()["email"] is None

    cliente.patch(f"/api/v1/clientes/{ana.id}", json={"activo": False})
    activos = cliente.get("/api/v1/clientes", params={"activo": True}).json()["data"]
    assert activos == []


def test_no_se_puede_vaciar_un_campo_obligatorio(cliente, recepcion_a, taller_a, crear_cliente):
    ana = crear_cliente(taller_a)
    respuesta = cliente.patch(f"/api/v1/clientes/{ana.id}", json={"nombre": None})
    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {"nombre"}


def test_la_autorizacion_no_se_puede_editar(cliente, recepcion_a, taller_a, crear_cliente):
    ana = crear_cliente(taller_a)
    cliente.patch(f"/api/v1/clientes/{ana.id}", json={"autoriza_datos": False})
    assert cliente.get(f"/api/v1/clientes/{ana.id}").json()["autoriza_datos"] is True


def test_mecanico_consulta_pero_no_crea_ni_edita(cliente, taller_a, crear_usuario, crear_cliente):
    ana = crear_cliente(taller_a)
    crear_usuario(taller_a, "mecanico@a.co", rol=RolUsuario.MECANICO)
    iniciar_sesion(cliente, "mecanico@a.co")

    assert cliente.get("/api/v1/clientes").status_code == 200
    assert cliente.get(f"/api/v1/clientes/{ana.id}").status_code == 200
    assert cliente.post("/api/v1/clientes", json=NUEVO_CLIENTE).status_code == 403
    assert cliente.patch(f"/api/v1/clientes/{ana.id}", json={"nombre": "X Y"}).status_code == 403


def test_sin_sesion_responde_401(cliente):
    assert cliente.get("/api/v1/clientes").status_code == 401


def test_aislamiento_cliente_de_otro_taller_no_existe(
    cliente, recepcion_a, taller_b, crear_cliente
):
    # ADR-006: leer o modificar un cliente ajeno responde 404, y no aparece en el listado.
    ajeno = crear_cliente(taller_b, "Cliente de B")

    assert cliente.get(f"/api/v1/clientes/{ajeno.id}").status_code == 404
    assert cliente.patch(f"/api/v1/clientes/{ajeno.id}", json={"activo": False}).status_code == 404
    assert cliente.get("/api/v1/clientes").json()["data"] == []


def test_cliente_creado_queda_en_el_taller_de_la_sesion(cliente, recepcion_a, taller_b):
    respuesta = cliente.post("/api/v1/clientes", json={**NUEVO_CLIENTE, "taller_id": taller_b.id})
    assert respuesta.status_code == 201
    assert cliente.get(f"/api/v1/clientes/{respuesta.json()['id']}").status_code == 200
