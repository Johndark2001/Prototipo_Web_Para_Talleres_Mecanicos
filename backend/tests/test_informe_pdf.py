"""Cambio #4B: informe PDF final, solo para órdenes ENTREGADAS."""

import re
import zlib

import pytest

from app.services.informe_pdf import _pesos
from tests.conftest import ADMIN, MECANICO, OTRO_MECANICO, RECEPCION, cambiar, codigo_error

CONFIRMAR = {"confirmacion": "ANONIMIZAR"}


def texto_pdf(contenido: bytes) -> str:
    """Texto de los flujos del PDF (fpdf2 los comprime con zlib)."""
    partes = []
    for flujo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", contenido, re.S):
        try:
            partes.append(zlib.decompress(flujo).decode("latin-1"))
        except zlib.error:
            partes.append(flujo.decode("latin-1"))
    return "\n".join(partes)


def ruta_informe(orden) -> str:
    return f"/api/v1/ordenes/{orden['id']}/informe.pdf"


def ruta_publica(orden) -> str:
    return f"/api/v1/seguimiento/{orden['codigo_seguimiento']}/informe.pdf"


def entregar(como, orden):
    mecanico = como(MECANICO)
    mecanico.patch(
        f"/api/v1/ordenes/{orden['id']}",
        json={"diagnostico": "Pastillas gastadas", "trabajo_realizado": "Cambio de pastillas"},
    )
    for estado in ("EN_DIAGNOSTICO", "REPARADO"):
        assert cambiar(mecanico, orden, estado).status_code == 201
    assert cambiar(como(RECEPCION), orden, "ENTREGADO").status_code == 201


@pytest.fixture
def orden_entregada(abrir_orden, como, taller_a, crear_repuesto):
    pastillas = crear_repuesto(taller_a, "PF01", nombre="Pastillas de freno", precio_venta="80000")
    orden = abrir_orden(
        motivo_ingreso=None,
        categoria_problema="Problemas de frenos",
        observacion_cliente="Ruido metálico al frenar",
        kilometraje=48900,
    )
    recepcion = como(RECEPCION)
    recepcion.post(
        f"/api/v1/ordenes/{orden['id']}/servicios",
        json={"descripcion": "Cambio de pastillas", "precio_unitario": "35000.50"},
    )
    recepcion.post(
        f"/api/v1/ordenes/{orden['id']}/repuestos",
        json={"repuesto_id": pastillas.id, "cantidad": "1"},
    )
    entregar(como, orden)
    return orden


def test_el_formato_de_pesos_es_colombiano():
    from decimal import Decimal

    assert _pesos(Decimal("143500.50")) == "$ 143.500,50"
    assert _pesos(Decimal("25000.00")) == "$ 25.000"


def test_el_taller_descarga_el_informe_completo(como, orden_entregada, ana):
    respuesta = como(RECEPCION).get(ruta_informe(orden_entregada))

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.headers["content-type"] == "application/pdf"
    assert respuesta.headers["content-disposition"] == (
        f'attachment; filename="informe-orden-{orden_entregada["numero"]}.pdf"'
    )
    assert respuesta.content.startswith(b"%PDF")
    texto = texto_pdf(respuesta.content)
    for esperado in (
        "Taller A",
        f"Orden #{orden_entregada['numero']}",
        ana.nombre,
        "ABC123",
        "48.900 km",
        "Problemas de frenos",
        "Ruido met",  # la tilde va codificada en Latin-1
        "Pastillas gastadas",
        "Cambio de pastillas",
        "Pastillas de freno",
        "$ 35.000,50",
        "$ 80.000",
        "$ 115.000,50",
        "Recibido",
        "Entregado",
        "Gracias por confiar",
    ):
        assert esperado in texto, esperado


@pytest.mark.parametrize("usuario", [ADMIN, MECANICO])
def test_admin_y_mecanico_asignado_tambien_lo_descargan(como, orden_entregada, usuario):
    assert como(usuario).get(ruta_informe(orden_entregada)).status_code == 200


def test_otro_mecanico_no_ve_el_informe(como, orden_entregada):
    assert como(OTRO_MECANICO).get(ruta_informe(orden_entregada)).status_code == 404


def test_sin_sesion_no_hay_informe_interno(cliente, orden_entregada):
    cliente.post("/api/v1/auth/logout", json={})
    assert cliente.get(ruta_informe(orden_entregada)).status_code == 401


@pytest.mark.parametrize(
    "estados",
    [
        (),
        ("EN_DIAGNOSTICO",),
        ("EN_DIAGNOSTICO", "ESPERANDO_REPUESTOS"),
        ("EN_DIAGNOSTICO", "REPARADO"),
    ],
)
def test_no_hay_informe_antes_de_entregar(abrir_orden, como, estados):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Listo"})
    for estado in estados:
        assert cambiar(mecanico, orden, estado).status_code == 201

    respuesta = como(RECEPCION).get(ruta_informe(orden))
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CONFLICTO"
    assert como(RECEPCION).get(ruta_publica(orden)).status_code == 409


def test_no_hay_informe_de_una_orden_cancelada(abrir_orden, como):
    orden = abrir_orden()
    cambiar(como(RECEPCION), orden, "CANCELADA", "El cliente no esperó")
    assert como(ADMIN).get(ruta_informe(orden)).status_code == 409


def test_el_portal_publico_entrega_el_informe_sin_datos_personales(cliente, orden_entregada, ana):
    cliente.post("/api/v1/auth/logout", json={})
    respuesta = cliente.get(ruta_publica(orden_entregada))

    assert respuesta.status_code == 200, respuesta.text
    texto = texto_pdf(respuesta.content)
    assert "Problemas de frenos" in texto
    assert "$ 115.000,50" in texto
    assert "ABC***" in texto
    for prohibido in (ana.nombre, ana.telefono, "ABC123", "48.900"):
        assert prohibido not in texto, prohibido


def test_codigo_publico_inexistente(cliente):
    assert (
        cliente.get("/api/v1/seguimiento/codigo-que-no-existe-1234/informe.pdf").status_code == 404
    )


def test_una_orden_anterior_al_catalogo_tambien_tiene_informe(abrir_orden, como):
    orden = abrir_orden()  # solo con motivo_ingreso, como antes del cambio #5
    entregar(como, orden)
    texto = texto_pdf(como(ADMIN).get(ruta_informe(orden)).content)
    assert "Sin categor" in texto
    assert "Ruido en la suspensi" in texto


def test_el_informe_de_un_cliente_anonimizado_no_tiene_sus_datos(abrir_orden, como, ana, equipo):
    orden = abrir_orden()
    entregar(como, orden)
    assert (
        como(ADMIN).post(f"/api/v1/clientes/{ana.id}/anonimizar", json=CONFIRMAR).status_code == 200
    )

    texto = texto_pdf(como(ADMIN).get(ruta_informe(orden)).content)
    assert "Cliente anonimizado" in texto
    assert "Ana G" not in texto
    assert "3001234567" not in texto


def test_textos_fuera_de_latin1_no_rompen_el_pdf(abrir_orden, como):
    orden = abrir_orden(motivo_ingreso="Ruido 🚗 “raro” — ya")
    entregar(como, orden)
    assert como(ADMIN).get(ruta_informe(orden)).status_code == 200
