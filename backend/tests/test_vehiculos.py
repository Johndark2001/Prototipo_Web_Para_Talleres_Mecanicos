import pytest

from app.models import RolUsuario
from tests.conftest import iniciar_sesion


@pytest.fixture
def recepcion_a(cliente, taller_a, crear_usuario):
    usuario = crear_usuario(taller_a, "recepcion@a.co", rol=RolUsuario.RECEPCION)
    iniciar_sesion(cliente, "recepcion@a.co")
    return usuario


@pytest.fixture
def ana(taller_a, crear_cliente):
    return crear_cliente(taller_a, "Ana Gómez")


def nuevo_vehiculo(cliente_id: int, **campos) -> dict:
    return {"placa": "abc-123", "marca": "Mazda", "modelo": "3", "cliente_id": cliente_id, **campos}


def campos_con_error(respuesta) -> set[str]:
    return {detalle["campo"] for detalle in respuesta.json()["error"]["details"]}


def test_crea_vehiculo_asociado_al_cliente_con_placa_normalizada(cliente, recepcion_a, ana):
    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id, anio=2015))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["placa"] == "ABC123"  # RN-20
    assert cuerpo["cliente"]["nombre"] == "Ana Gómez"
    detalle = cliente.get(f"/api/v1/clientes/{ana.id}").json()
    assert [v["placa"] for v in detalle["vehiculos"]] == ["ABC123"]


@pytest.mark.parametrize("escrita", ["ABC123", "abc 123", " Abc-123 "])
def test_placa_duplicada_responde_422_aunque_se_escriba_distinto(
    cliente, recepcion_a, ana, escrita
):
    cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id))

    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id, placa=escrita))

    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {"placa"}


def test_placa_de_carro_inactivo_avisa_que_se_reactive(cliente, recepcion_a, ana, crear_vehiculo):
    crear_vehiculo(ana, "ABC123", activo=False)
    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id))
    assert respuesta.status_code == 422
    assert "inactivo" in respuesta.json()["error"]["details"][0]["mensaje"]


def test_misma_placa_se_permite_en_otro_taller(
    cliente, recepcion_a, ana, taller_b, crear_cliente, crear_vehiculo
):
    crear_vehiculo(crear_cliente(taller_b), "ABC123")
    assert cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id)).status_code == 201


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("placa", "AB"), ("placa", "ABC*12"), ("anio", 1900), ("anio", 2101), ("marca", " ")],
)
def test_datos_invalidos_responden_422_con_el_campo(cliente, recepcion_a, ana, campo, valor):
    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id, **{campo: valor}))
    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {campo}


def test_no_se_asocia_a_un_cliente_inactivo(cliente, recepcion_a, taller_a, crear_cliente):
    inactivo = crear_cliente(taller_a, activo=False)
    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(inactivo.id))
    assert respuesta.status_code == 422
    assert campos_con_error(respuesta) == {"cliente_id"}


def test_busqueda_por_placa_parcial_y_normalizada(cliente, recepcion_a, ana, crear_vehiculo):
    crear_vehiculo(ana, "ABC1234")
    crear_vehiculo(ana, "ABC123")
    crear_vehiculo(ana, "XYZ987")

    def placas(texto):
        datos = cliente.get("/api/v1/vehiculos", params={"placa": texto}).json()["data"]
        return [v["placa"] for v in datos]

    assert placas("abc-123") == ["ABC123", "ABC1234"]  # la coincidencia exacta va primero
    assert placas("987") == ["XYZ987"]
    assert placas("QQQ") == []


def test_cambio_de_dueno(cliente, recepcion_a, ana, taller_a, crear_cliente, crear_vehiculo):
    carro = crear_vehiculo(ana, "ABC123")
    pedro = crear_cliente(taller_a, "Pedro Ruiz")

    respuesta = cliente.patch(f"/api/v1/vehiculos/{carro.id}", json={"cliente_id": pedro.id})

    assert respuesta.status_code == 200
    assert respuesta.json()["cliente"]["nombre"] == "Pedro Ruiz"
    assert cliente.get(f"/api/v1/clientes/{ana.id}").json()["vehiculos"] == []
    filtro = cliente.get("/api/v1/vehiculos", params={"cliente_id": pedro.id}).json()
    assert [v["placa"] for v in filtro["data"]] == ["ABC123"]


def test_editar_placa_respeta_la_unicidad(cliente, recepcion_a, ana, crear_vehiculo):
    crear_vehiculo(ana, "ABC123")
    otro = crear_vehiculo(ana, "XYZ987")

    repetida = cliente.patch(f"/api/v1/vehiculos/{otro.id}", json={"placa": "abc 123"})
    corregida = cliente.patch(f"/api/v1/vehiculos/{otro.id}", json={"placa": "xyz-988"})

    assert repetida.status_code == 422
    assert corregida.status_code == 200
    assert corregida.json()["placa"] == "XYZ988"


def test_desactivar_vehiculo(cliente, recepcion_a, ana, crear_vehiculo):
    carro = crear_vehiculo(ana)
    respuesta = cliente.patch(f"/api/v1/vehiculos/{carro.id}", json={"activo": False})
    assert respuesta.json()["activo"] is False
    assert cliente.get("/api/v1/vehiculos", params={"activo": True}).json()["data"] == []


def test_mecanico_consulta_pero_no_crea_ni_edita(
    cliente, taller_a, ana, crear_usuario, crear_vehiculo
):
    carro = crear_vehiculo(ana)
    crear_usuario(taller_a, "mecanico@a.co", rol=RolUsuario.MECANICO)
    iniciar_sesion(cliente, "mecanico@a.co")

    assert cliente.get("/api/v1/vehiculos", params={"placa": "ABC"}).status_code == 200
    assert cliente.get(f"/api/v1/vehiculos/{carro.id}").status_code == 200
    assert cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id)).status_code == 403
    assert cliente.patch(f"/api/v1/vehiculos/{carro.id}", json={"color": "Rojo"}).status_code == 403


def test_aislamiento_vehiculo_de_otro_taller_no_existe(
    cliente, recepcion_a, taller_b, crear_cliente, crear_vehiculo
):
    ajeno = crear_vehiculo(crear_cliente(taller_b), "ABC123")

    assert cliente.get(f"/api/v1/vehiculos/{ajeno.id}").status_code == 404
    assert cliente.patch(f"/api/v1/vehiculos/{ajeno.id}", json={"activo": False}).status_code == 404
    assert cliente.get("/api/v1/vehiculos", params={"placa": "ABC123"}).json()["data"] == []


def test_aislamiento_no_se_asocia_a_cliente_de_otro_taller(
    cliente, recepcion_a, ana, taller_b, crear_cliente, crear_vehiculo
):
    # ADR-006 punto 3: la referencia cruzada a otro taller responde "no encontrado".
    ajeno = crear_cliente(taller_b, "Cliente de B")
    carro = crear_vehiculo(ana)

    crear = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ajeno.id, placa="QWE123"))
    reasignar = cliente.patch(f"/api/v1/vehiculos/{carro.id}", json={"cliente_id": ajeno.id})

    assert crear.status_code == 404
    assert reasignar.status_code == 404
    assert cliente.get(f"/api/v1/vehiculos/{carro.id}").json()["cliente"]["id"] == ana.id


@pytest.mark.parametrize("vacio", [None, ""])
def test_anio_y_color_son_opcionales(cliente, recepcion_a, ana, vacio):
    # Regresión: con el año vacío la validación lanzaba TypeError y la API respondía 500.
    respuesta = cliente.post(
        "/api/v1/vehiculos", json=nuevo_vehiculo(ana.id, placa="DEF456", anio=vacio, color=vacio)
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["anio"] is None
    assert respuesta.json()["color"] is None


def test_editar_permite_borrar_anio_y_color(cliente, recepcion_a, ana, crear_vehiculo):
    carro = crear_vehiculo(ana, anio=2015, color="Rojo")

    respuesta = cliente.patch(f"/api/v1/vehiculos/{carro.id}", json={"anio": "", "color": None})

    assert respuesta.status_code == 200
    assert respuesta.json()["anio"] is None
    assert respuesta.json()["color"] is None


@pytest.mark.parametrize(
    ("valor", "mensaje"),
    [
        (1949, "Debe ser mayor o igual a 1950"),
        (2101, "Debe ser menor o igual a 2100"),
        ("abc", "Debe ser un número entero"),
    ],
)
def test_anio_invalido_muestra_mensaje_claro(cliente, recepcion_a, ana, valor, mensaje):
    respuesta = cliente.post("/api/v1/vehiculos", json=nuevo_vehiculo(ana.id, anio=valor))

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"] == [{"campo": "anio", "mensaje": mensaje}]
