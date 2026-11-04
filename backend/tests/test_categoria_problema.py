"""Cambio #5: categoría del problema según el tipo de vehículo y observación del cliente."""

import pytest

from app.models import TipoVehiculo
from app.services import categorias
from tests.conftest import ADMIN, MECANICO, RECEPCION, codigo_error


def abrir(cliente, vehiculo, **campos):
    return cliente.post("/api/v1/ordenes", json={"vehiculo_id": vehiculo.id, **campos})


def detalle_error(respuesta):
    return {d["campo"]: d["mensaje"] for d in respuesta.json()["error"]["details"]}


@pytest.fixture
def moto(ana, crear_vehiculo):
    return crear_vehiculo(ana, "XYZ12D", tipo=TipoVehiculo.MOTO, marca="Yamaha", modelo="FZ")


@pytest.mark.parametrize(
    ("texto", "esperada"),
    [
        ("bateria", "Problemas de batería"),
        ("BATERÍA", "Problemas de batería"),
        ("fren", "Problemas de frenos"),
        ("trans", "Problemas de transmisión"),
    ],
)
def test_el_buscador_ignora_tildes_y_mayusculas(texto, esperada):
    assert esperada in categorias.buscar(TipoVehiculo.CARRO, texto)


def test_las_listas_dependen_del_tipo_y_terminan_en_otro():
    carro = categorias.CATEGORIAS[TipoVehiculo.CARRO]
    moto = categorias.CATEGORIAS[TipoVehiculo.MOTO]
    assert "Aire acondicionado" in carro and "Aire acondicionado" not in moto
    assert "Kit de arrastre" in moto and "Kit de arrastre" not in carro
    assert carro[-1] == moto[-1] == "Otro"
    assert len(carro) == 22 and len(moto) == 20


def test_el_catalogo_se_consulta_con_sesion(como, equipo, cliente):
    assert cliente.get("/api/v1/catalogos/categorias-problema").status_code == 401
    respuesta = como(MECANICO).get("/api/v1/catalogos/categorias-problema")
    assert respuesta.status_code == 200
    assert "Cadena de transmisión" in respuesta.json()["MOTO"]


def test_recepcion_registra_categoria_y_observacion(como, equipo, carro):
    respuesta = abrir(
        como(RECEPCION),
        carro,
        categoria_problema="Problemas de frenos",
        observacion_cliente="El cliente indica que escucha un ruido metálico al frenar.",
    )

    assert respuesta.status_code == 201, respuesta.text
    orden = respuesta.json()
    assert orden["categoria_problema"] == "Problemas de frenos"
    assert orden["categoria_otro"] is None
    assert orden["observacion_cliente"].startswith("El cliente indica")
    # El motivo compuesto mantiene funcionando las listas y el dashboard.
    assert orden["motivo_ingreso"] == (
        "Problemas de frenos — El cliente indica que escucha un ruido metálico al frenar."
    )


def test_la_categoria_se_guarda_con_el_nombre_del_catalogo(como, equipo, carro):
    orden = abrir(como(ADMIN), carro, categoria_problema="problemas de bateria").json()
    assert orden["categoria_problema"] == "Problemas de batería"
    assert orden["motivo_ingreso"] == "Problemas de batería"


def test_la_categoria_debe_ser_del_tipo_de_vehiculo(como, equipo, moto):
    respuesta = abrir(como(RECEPCION), moto, categoria_problema="Aire acondicionado")
    assert respuesta.status_code == 422
    assert "moto" in detalle_error(respuesta)["categoria_problema"]

    assert abrir(como(RECEPCION), moto, categoria_problema="Kit de arrastre").status_code == 201


def test_otro_exige_describir_el_problema(como, equipo, carro):
    sin_detalle = abrir(como(RECEPCION), carro, categoria_problema="Otro")
    assert sin_detalle.status_code == 422
    assert "categoria_otro" in detalle_error(sin_detalle)

    orden = abrir(
        como(RECEPCION), carro, categoria_problema="Otro", categoria_otro="Vidrio eléctrico"
    ).json()
    assert (orden["categoria_problema"], orden["categoria_otro"]) == ("Otro", "Vidrio eléctrico")
    assert orden["motivo_ingreso"] == "Otro: Vidrio eléctrico"


def test_el_detalle_de_otro_se_descarta_en_otra_categoria(como, equipo, carro):
    orden = abrir(
        como(RECEPCION), carro, categoria_problema="Cambio de aceite", categoria_otro="x"
    ).json()
    assert orden["categoria_otro"] is None


def test_sin_categoria_ni_motivo_no_se_abre(como, equipo, carro):
    respuesta = abrir(como(RECEPCION), carro, observacion_cliente="Algo suena")
    assert respuesta.status_code == 422
    assert "categoria_problema" in detalle_error(respuesta)


def test_el_motivo_libre_anterior_sigue_funcionando(como, equipo, carro):
    orden = abrir(como(RECEPCION), carro, motivo_ingreso="Ruido en la suspensión").json()
    assert orden["categoria_problema"] is None
    assert orden["observacion_cliente"] == "Ruido en la suspensión"


def test_recepcion_corrige_la_categoria_y_se_recompone_el_motivo(como, equipo, carro):
    orden = abrir(como(RECEPCION), carro, categoria_problema="Problemas de motor").json()
    respuesta = como(RECEPCION).patch(
        f"/api/v1/ordenes/{orden['id']}",
        json={"categoria_problema": "Sobrecalentamiento", "observacion_cliente": "Sube la aguja"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["motivo_ingreso"] == "Sobrecalentamiento — Sube la aguja"


def test_una_orden_anterior_recibe_categoria_al_corregirla(como, equipo, carro):
    orden = abrir(como(RECEPCION), carro, motivo_ingreso="Revisión de frenos").json()
    respuesta = como(ADMIN).patch(
        f"/api/v1/ordenes/{orden['id']}", json={"categoria_problema": "Problemas de frenos"}
    )

    datos = respuesta.json()
    assert datos["categoria_problema"] == "Problemas de frenos"
    assert datos["observacion_cliente"] == "Revisión de frenos"


def test_el_mecanico_no_registra_el_problema(abrir_orden, como):
    orden = abrir_orden()
    respuesta = como(MECANICO).patch(
        f"/api/v1/ordenes/{orden['id']}", json={"categoria_problema": "Problemas de motor"}
    )
    assert respuesta.status_code == 403
    assert codigo_error(respuesta) == "SIN_PERMISO"


def test_la_categoria_no_se_puede_vaciar(como, equipo, carro):
    orden = abrir(como(RECEPCION), carro, categoria_problema="Problemas de motor").json()
    respuesta = como(RECEPCION).patch(
        f"/api/v1/ordenes/{orden['id']}", json={"categoria_problema": None}
    )
    assert respuesta.status_code == 422
