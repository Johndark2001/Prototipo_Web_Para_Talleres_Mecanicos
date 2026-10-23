from app.models import RolUsuario, Usuario
from tests.conftest import iniciar_sesion


def test_login_correcto_crea_cookie_segura_y_devuelve_sesion(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "admin@a.co")

    respuesta = iniciar_sesion(cliente, "admin@a.co")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["usuario"]["email"] == "admin@a.co"
    assert cuerpo["usuario"]["rol"] == "ADMIN"
    assert cuerpo["taller"]["nombre"] == "Taller A"
    assert "password_hash" not in cuerpo["usuario"]
    cookie = respuesta.headers["set-cookie"].lower()
    assert cookie.startswith("sesion=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_login_ignora_mayusculas_en_el_correo(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "admin@a.co")
    assert iniciar_sesion(cliente, "  Admin@A.CO ").status_code == 200


def test_clave_incorrecta_y_correo_inexistente_dan_el_mismo_mensaje(
    cliente, taller_a, crear_usuario
):
    crear_usuario(taller_a, "admin@a.co")

    clave_mala = iniciar_sesion(cliente, "admin@a.co", "otra-clave")
    correo_malo = iniciar_sesion(cliente, "nadie@a.co")

    assert clave_mala.status_code == correo_malo.status_code == 401
    assert clave_mala.json() == correo_malo.json()
    assert clave_mala.json()["error"]["code"] == "NO_AUTENTICADO"
    assert "set-cookie" not in clave_mala.headers


def test_usuario_inactivo_no_puede_iniciar_sesion(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "inactivo@a.co", activo=False)
    assert iniciar_sesion(cliente, "inactivo@a.co").status_code == 401


def test_la_clave_se_guarda_con_hash_argon2id(db, taller_a, crear_usuario):
    usuario = crear_usuario(taller_a, "admin@a.co")
    guardado = db.get(Usuario, usuario.id)
    assert guardado.password_hash.startswith("$argon2id$")
    assert "clave-segura-1" not in guardado.password_hash


def test_me_sin_sesion_responde_401(cliente):
    respuesta = cliente.get("/api/v1/auth/me")
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["code"] == "NO_AUTENTICADO"


def test_me_con_sesion_devuelve_usuario_y_taller(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "mecanico@a.co", rol=RolUsuario.MECANICO)
    iniciar_sesion(cliente, "mecanico@a.co")

    respuesta = cliente.get("/api/v1/auth/me")

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["rol"] == "MECANICO"
    assert respuesta.json()["taller"]["id"] == taller_a.id


def test_logout_borra_la_sesion(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "admin@a.co")
    iniciar_sesion(cliente, "admin@a.co")

    assert cliente.post("/api/v1/auth/logout", json={}).status_code == 204
    assert cliente.get("/api/v1/auth/me").status_code == 401


def test_token_alterado_es_rechazado(cliente, taller_a, crear_usuario):
    crear_usuario(taller_a, "admin@a.co")
    iniciar_sesion(cliente, "admin@a.co")
    token = cliente.cookies.get("sesion")
    cliente.cookies.clear()
    cliente.cookies.set("sesion", token[:-2] + "xx")

    assert cliente.get("/api/v1/auth/me").status_code == 401


def test_desactivar_usuario_corta_su_sesion_de_inmediato(db, cliente, taller_a, crear_usuario):
    usuario = crear_usuario(taller_a, "recepcion@a.co", rol=RolUsuario.RECEPCION)
    iniciar_sesion(cliente, "recepcion@a.co")
    assert cliente.get("/api/v1/auth/me").status_code == 200

    usuario.activo = False
    db.commit()

    assert cliente.get("/api/v1/auth/me").status_code == 401


def test_modificaciones_sin_json_son_rechazadas(cliente):
    respuesta = cliente.post(
        "/api/v1/auth/login",
        content="email=a@a.co&password=x",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert respuesta.status_code == 415
    assert respuesta.json()["error"]["code"] == "TIPO_NO_SOPORTADO"


def test_datos_invalidos_usan_el_formato_de_error_unico(cliente):
    respuesta = cliente.post("/api/v1/auth/login", json={"email": "no-es-correo"})

    assert respuesta.status_code == 422
    error = respuesta.json()["error"]
    assert error["code"] == "DATOS_INVALIDOS"
    campos = {detalle["campo"] for detalle in error["details"]}
    assert campos == {"email", "password"}


def test_salud_confirma_conexion_a_la_base(cliente):
    respuesta = cliente.get("/api/v1/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "base_de_datos": "ok"}
