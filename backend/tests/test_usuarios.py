import pytest

from app.models import RolUsuario
from tests.conftest import iniciar_sesion

NUEVO_MECANICO = {
    "nombre": "Juan Pérez",
    "email": "juan@a.co",
    "password": "clave-de-juan",
    "rol": "MECANICO",
}


@pytest.fixture
def admin_a(cliente, taller_a, crear_usuario):
    usuario = crear_usuario(taller_a, "admin@a.co")
    iniciar_sesion(cliente, "admin@a.co")
    return usuario


def test_admin_crea_usuario_que_luego_puede_iniciar_sesion(cliente, admin_a):
    respuesta = cliente.post("/api/v1/usuarios", json=NUEVO_MECANICO)

    assert respuesta.status_code == 201
    assert respuesta.json()["rol"] == "MECANICO"
    cliente.post("/api/v1/auth/logout", json={})
    assert iniciar_sesion(cliente, "juan@a.co", "clave-de-juan").status_code == 200


def test_correo_duplicado_responde_409(cliente, admin_a):
    cliente.post("/api/v1/usuarios", json=NUEVO_MECANICO)
    respuesta = cliente.post("/api/v1/usuarios", json={**NUEVO_MECANICO, "email": "JUAN@a.co"})
    assert respuesta.status_code == 409


def test_clave_corta_es_rechazada(cliente, admin_a):
    respuesta = cliente.post("/api/v1/usuarios", json={**NUEVO_MECANICO, "password": "corta"})
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "password"


@pytest.mark.parametrize("rol", [RolUsuario.RECEPCION, RolUsuario.MECANICO])
def test_solo_admin_gestiona_usuarios(cliente, taller_a, crear_usuario, rol):
    crear_usuario(taller_a, "otro@a.co", rol=rol)
    iniciar_sesion(cliente, "otro@a.co")

    assert cliente.get("/api/v1/usuarios").status_code == 403
    assert cliente.post("/api/v1/usuarios", json=NUEVO_MECANICO).status_code == 403


def test_listado_solo_muestra_usuarios_del_propio_taller(
    cliente, admin_a, taller_a, taller_b, crear_usuario
):
    crear_usuario(taller_a, "mecanico@a.co", rol=RolUsuario.MECANICO)
    crear_usuario(taller_b, "admin@b.co")

    cuerpo = cliente.get("/api/v1/usuarios").json()

    correos = {usuario["email"] for usuario in cuerpo["data"]}
    assert correos == {"admin@a.co", "mecanico@a.co"}
    assert cuerpo["pagination"]["total_items"] == 2


def test_usuario_creado_queda_en_el_taller_del_admin(cliente, admin_a, taller_b):
    # Aunque se intente enviar otro taller, el taller sale de la sesión (ADR-006).
    respuesta = cliente.post("/api/v1/usuarios", json={**NUEVO_MECANICO, "taller_id": taller_b.id})
    assert respuesta.status_code == 201

    correos = {u["email"] for u in cliente.get("/api/v1/usuarios").json()["data"]}
    assert "juan@a.co" in correos


def test_admin_no_puede_modificar_usuarios_de_otro_taller(
    cliente, admin_a, taller_b, crear_usuario
):
    ajeno = crear_usuario(taller_b, "admin@b.co")

    respuesta = cliente.patch(f"/api/v1/usuarios/{ajeno.id}", json={"activo": False})

    assert respuesta.status_code == 404


def test_admin_cambia_rol_y_desactiva_a_otro_usuario(cliente, admin_a, taller_a, crear_usuario):
    otro = crear_usuario(taller_a, "otro@a.co", rol=RolUsuario.MECANICO)

    respuesta = cliente.patch(
        f"/api/v1/usuarios/{otro.id}", json={"rol": "RECEPCION", "activo": False}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "RECEPCION"
    assert respuesta.json()["activo"] is False


@pytest.mark.parametrize("cambio", [{"activo": False}, {"rol": "MECANICO"}])
def test_admin_no_puede_quitarse_su_propio_acceso(cliente, admin_a, cambio):
    respuesta = cliente.patch(f"/api/v1/usuarios/{admin_a.id}", json=cambio)
    assert respuesta.status_code == 409


def test_paginacion_respeta_el_tamano_de_pagina(cliente, admin_a, taller_a, crear_usuario):
    for i in range(3):
        crear_usuario(taller_a, f"m{i}@a.co", rol=RolUsuario.MECANICO)

    cuerpo = cliente.get("/api/v1/usuarios", params={"page": 2, "page_size": 3}).json()

    assert len(cuerpo["data"]) == 1
    assert cuerpo["pagination"] == {
        "page": 2,
        "page_size": 3,
        "total_items": 4,
        "total_pages": 2,
    }
