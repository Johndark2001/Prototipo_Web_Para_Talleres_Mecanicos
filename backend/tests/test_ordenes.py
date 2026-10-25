from datetime import date, timedelta

import pytest

from app.models import RolUsuario
from tests.conftest import iniciar_sesion

ADMIN, RECEPCION, MECANICO, OTRO_MECANICO = (
    "admin@a.co",
    "recepcion@a.co",
    "mecanico@a.co",
    "otro.mecanico@a.co",
)


@pytest.fixture
def equipo(taller_a, crear_usuario):
    return {
        "admin": crear_usuario(taller_a, ADMIN),
        "recepcion": crear_usuario(taller_a, RECEPCION, rol=RolUsuario.RECEPCION),
        "mecanico": crear_usuario(taller_a, MECANICO, rol=RolUsuario.MECANICO),
        "otro": crear_usuario(taller_a, OTRO_MECANICO, rol=RolUsuario.MECANICO),
    }


@pytest.fixture
def ana(taller_a, crear_cliente):
    return crear_cliente(taller_a, "Ana Gómez")


@pytest.fixture
def carro(ana, crear_vehiculo):
    return crear_vehiculo(ana, "ABC123")


@pytest.fixture
def como(cliente):
    """Cambia la sesión del cliente HTTP al usuario indicado."""

    def _como(email: str):
        assert iniciar_sesion(cliente, email).status_code == 200
        return cliente

    return _como


@pytest.fixture
def abrir_orden(como, equipo, carro):
    def _abrir(vehiculo=carro, con_mecanico=True, **campos):
        cuerpo = {"vehiculo_id": vehiculo.id, "motivo_ingreso": "Ruido en la suspensión", **campos}
        if con_mecanico:
            cuerpo["mecanico_id"] = equipo["mecanico"].id
        respuesta = como(RECEPCION).post("/api/v1/ordenes", json=cuerpo)
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()

    return _abrir


def cambiar(cliente, orden, estado, nota=None):
    return cliente.post(
        f"/api/v1/ordenes/{orden['id']}/historial", json={"estado": estado, "nota": nota}
    )


def codigo_error(respuesta) -> str:
    return respuesta.json()["error"]["code"]


# --- Recepción (RF-05) -------------------------------------------------------------------


def test_recepcion_abre_orden_en_recibido_con_historial_y_asignacion(abrir_orden, equipo):
    orden = abrir_orden(kilometraje="48900", fecha_entrega_estimada="")

    assert orden["numero"] == 1
    assert orden["estado"] == "RECIBIDO"
    assert orden["kilometraje"] == 48900
    assert orden["cliente"]["nombre"] == "Ana Gómez"
    assert orden["mecanico"]["id"] == equipo["mecanico"].id
    assert orden["creador"]["id"] == equipo["recepcion"].id
    assert [(h["estado_anterior"], h["estado_nuevo"]) for h in orden["historial"]] == [
        (None, "RECIBIDO")
    ]
    assert len(orden["asignaciones"]) == 1
    # 128 bits en base64 para URL: 22 caracteres (RN-12, ADR-005).
    assert len(orden["codigo_seguimiento"]) == 22


def test_numero_consecutivo_por_taller(
    abrir_orden, ana, crear_vehiculo, taller_b, crear_cliente, crear_usuario, como
):
    primera = abrir_orden()
    segunda = abrir_orden(vehiculo=crear_vehiculo(ana, "XYZ987"))
    crear_usuario(taller_b, "admin@b.co")
    carro_b = crear_vehiculo(crear_cliente(taller_b), "QWE123")
    en_b = como("admin@b.co").post(
        "/api/v1/ordenes", json={"vehiculo_id": carro_b.id, "motivo_ingreso": "Aceite"}
    )

    assert (primera["numero"], segunda["numero"]) == (1, 2)
    assert en_b.json()["numero"] == 1  # cada taller lleva su propio consecutivo
    assert primera["codigo_seguimiento"] != segunda["codigo_seguimiento"]


def test_un_carro_solo_tiene_una_orden_abierta(abrir_orden, como, carro):
    # RN-08
    primera = abrir_orden()

    respuesta = como(RECEPCION).post(
        "/api/v1/ordenes", json={"vehiculo_id": carro.id, "motivo_ingreso": "Otra cosa"}
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["details"]["orden_id"] == primera["id"]


def test_al_entregar_o_cancelar_el_carro_puede_volver_a_entrar(abrir_orden, como):
    orden = abrir_orden(con_mecanico=False)
    cambiar(como(RECEPCION), orden, "CANCELADA", "El cliente no esperó")

    assert abrir_orden()["numero"] == 2


@pytest.mark.parametrize(
    ("campos", "campo_error"),
    [
        ({"motivo_ingreso": " "}, "motivo_ingreso"),
        ({"kilometraje": -1}, "kilometraje"),
        (
            {"fecha_entrega_estimada": str(date.today() - timedelta(days=1))},
            "fecha_entrega_estimada",
        ),
    ],
)
def test_datos_de_recepcion_invalidos(como, equipo, carro, campos, campo_error):
    cuerpo = {"vehiculo_id": carro.id, "motivo_ingreso": "Revisión", **campos}
    respuesta = como(RECEPCION).post("/api/v1/ordenes", json=cuerpo)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == campo_error


@pytest.mark.parametrize("inactivo", ["vehiculo", "dueno"])
def test_no_se_recibe_un_carro_o_dueno_inactivo(como, equipo, ana, crear_vehiculo, db, inactivo):
    vehiculo = crear_vehiculo(ana, "INA123", activo=inactivo != "vehiculo")
    if inactivo == "dueno":
        ana.activo = False
        db.commit()

    respuesta = como(RECEPCION).post(
        "/api/v1/ordenes", json={"vehiculo_id": vehiculo.id, "motivo_ingreso": "Frenos"}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["details"][0]["campo"] == "vehiculo_id"


def test_solo_se_asigna_un_mecanico_activo(como, equipo, carro, db):
    cuerpo = {"vehiculo_id": carro.id, "motivo_ingreso": "Frenos"}
    con_recepcionista = como(ADMIN).post(
        "/api/v1/ordenes", json={**cuerpo, "mecanico_id": equipo["recepcion"].id}
    )
    equipo["otro"].activo = False
    db.commit()
    con_inactivo = como(ADMIN).post(
        "/api/v1/ordenes", json={**cuerpo, "mecanico_id": equipo["otro"].id}
    )

    assert con_recepcionista.status_code == 422
    assert con_inactivo.status_code == 422


def test_el_mecanico_no_abre_ordenes(como, equipo, carro):
    respuesta = como(MECANICO).post(
        "/api/v1/ordenes", json={"vehiculo_id": carro.id, "motivo_ingreso": "Frenos"}
    )
    assert respuesta.status_code == 403


def test_la_orden_conserva_al_dueno_de_ese_momento(
    abrir_orden, como, carro, taller_a, crear_cliente
):
    orden = abrir_orden()
    pedro = crear_cliente(taller_a, "Pedro Ruiz")
    como(ADMIN).patch(f"/api/v1/vehiculos/{carro.id}", json={"cliente_id": pedro.id})

    assert como(ADMIN).get(f"/api/v1/ordenes/{orden['id']}").json()["cliente"]["nombre"] == (
        "Ana Gómez"
    )


# --- Estados (RF-06, §7) ------------------------------------------------------------------


def test_flujo_completo_pasando_por_esperando_repuestos(abrir_orden, como):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    assert cambiar(mecanico, orden, "EN_DIAGNOSTICO").status_code == 201
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"diagnostico": "Buje gastado"})
    assert cambiar(mecanico, orden, "ESPERANDO_REPUESTOS", "Falta buje").status_code == 201
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Cambio de buje"})
    assert cambiar(mecanico, orden, "REPARADO").status_code == 201

    entregada = cambiar(como(RECEPCION), orden, "ENTREGADO")

    assert entregada.status_code == 201
    cuerpo = entregada.json()
    assert cuerpo["fecha_entrega"] is not None
    assert [h["estado_nuevo"] for h in cuerpo["historial"]] == [
        "RECIBIDO",
        "EN_DIAGNOSTICO",
        "ESPERANDO_REPUESTOS",
        "REPARADO",
        "ENTREGADO",
    ]
    assert cuerpo["historial"][2]["nota"] == "Falta buje"
    assert cuerpo["transiciones"] == []


def test_flujo_corto_sin_esperar_repuestos(abrir_orden, como):
    orden = abrir_orden()
    admin = como(ADMIN)
    cambiar(admin, orden, "EN_DIAGNOSTICO")
    admin.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Ajuste"})
    assert cambiar(admin, orden, "REPARADO").status_code == 201


def test_rn13_sin_mecanico_no_inicia_diagnostico(abrir_orden, como):
    orden = abrir_orden(con_mecanico=False)
    respuesta = cambiar(como(ADMIN), orden, "EN_DIAGNOSTICO")
    assert respuesta.status_code == 409
    assert "mecánico" in respuesta.json()["error"]["message"]


@pytest.mark.parametrize("trabajo", [None, "   "])
def test_rn17_sin_trabajo_realizado_no_pasa_a_reparado(abrir_orden, como, trabajo):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    cambiar(mecanico, orden, "EN_DIAGNOSTICO")
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": trabajo})

    respuesta = cambiar(mecanico, orden, "REPARADO")

    assert respuesta.status_code == 409
    assert "trabajo realizado" in respuesta.json()["error"]["message"]


def test_transicion_invalida_responde_409(abrir_orden, como):
    orden = abrir_orden()
    respuesta = cambiar(como(ADMIN), orden, "REPARADO")
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CONFLICTO"


def test_no_se_vuelve_de_esperando_repuestos_a_diagnostico(abrir_orden, como):
    # H-1: ni siquiera el ADMIN, con nota.
    orden = abrir_orden()
    mecanico = como(MECANICO)
    cambiar(mecanico, orden, "EN_DIAGNOSTICO")
    cambiar(mecanico, orden, "ESPERANDO_REPUESTOS")

    respuesta = cambiar(como(ADMIN), orden, "EN_DIAGNOSTICO", "Me equivoqué")

    assert respuesta.status_code == 409


@pytest.mark.parametrize(
    ("usuario", "estado"),
    [
        (RECEPCION, "EN_DIAGNOSTICO"),  # el cambio de taller es del mecánico o del ADMIN
        (OTRO_MECANICO, "EN_DIAGNOSTICO"),  # no es su orden: ni siquiera la ve
        (MECANICO, "CANCELADA"),  # cancelar es de ADMIN o RECEPCION
    ],
)
def test_permisos_de_cambio_de_estado(abrir_orden, como, usuario, estado):
    orden = abrir_orden()
    respuesta = cambiar(como(usuario), orden, estado, "nota")
    assert respuesta.status_code == (404 if usuario == OTRO_MECANICO else 403)


def test_el_mecanico_no_entrega(abrir_orden, como):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    cambiar(mecanico, orden, "EN_DIAGNOSTICO")
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Listo"})
    cambiar(mecanico, orden, "REPARADO")

    assert cambiar(mecanico, orden, "ENTREGADO").status_code == 403


def test_rn18_cancelar_exige_motivo(abrir_orden, como):
    orden = abrir_orden()
    recepcion = como(RECEPCION)

    sin_motivo = cambiar(recepcion, orden, "CANCELADA")
    con_motivo = cambiar(recepcion, orden, "CANCELADA", "El cliente se llevó el carro")

    assert sin_motivo.status_code == 422
    assert sin_motivo.json()["error"]["details"][0]["campo"] == "nota"
    assert con_motivo.json()["motivo_cancelacion"] == "El cliente se llevó el carro"


def test_rn07_orden_finalizada_no_se_modifica(abrir_orden, como, equipo):
    orden = abrir_orden()
    admin = como(ADMIN)
    cambiar(admin, orden, "CANCELADA", "Duplicada")
    ruta = f"/api/v1/ordenes/{orden['id']}"

    assert admin.patch(ruta, json={"diagnostico": "x"}).status_code == 409
    assert cambiar(admin, orden, "RECIBIDO", "volver").status_code == 409
    asignar = admin.post(f"{ruta}/asignaciones", json={"mecanico_id": equipo["otro"].id})
    assert asignar.status_code == 409


def test_admin_devuelve_un_paso_con_nota_obligatoria(abrir_orden, como):
    orden = abrir_orden()
    cambiar(como(MECANICO), orden, "EN_DIAGNOSTICO")
    admin = como(ADMIN)

    sin_nota = cambiar(admin, orden, "RECIBIDO")
    con_nota = cambiar(admin, orden, "RECIBIDO", "Se inició por error")

    assert sin_nota.status_code == 422
    assert con_nota.status_code == 201
    ultimo = con_nota.json()["historial"][-1]
    assert (ultimo["estado_anterior"], ultimo["estado_nuevo"]) == ("EN_DIAGNOSTICO", "RECIBIDO")


def test_reparado_vuelve_al_estado_del_que_llego(abrir_orden, como):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    cambiar(mecanico, orden, "EN_DIAGNOSTICO")
    cambiar(mecanico, orden, "ESPERANDO_REPUESTOS")
    mecanico.patch(f"/api/v1/ordenes/{orden['id']}", json={"trabajo_realizado": "Listo"})
    cambiar(mecanico, orden, "REPARADO")
    admin = como(ADMIN)

    detalle = admin.get(f"/api/v1/ordenes/{orden['id']}").json()
    retrocesos = [t["estado"] for t in detalle["transiciones"] if t["tipo"] == "RETROCESO"]

    assert retrocesos == ["ESPERANDO_REPUESTOS"]
    assert cambiar(admin, orden, "EN_DIAGNOSTICO", "x").status_code == 409


def test_la_respuesta_ofrece_solo_las_transiciones_validas(abrir_orden, como):
    orden = abrir_orden()

    def ofrecidas(email):
        detalle = como(email).get(f"/api/v1/ordenes/{orden['id']}").json()
        return [t["estado"] for t in detalle["transiciones"]]

    assert ofrecidas(MECANICO) == ["EN_DIAGNOSTICO"]
    assert ofrecidas(RECEPCION) == ["CANCELADA"]
    assert ofrecidas(ADMIN) == ["EN_DIAGNOSTICO", "CANCELADA"]


# --- Trabajo, asignación y "Mis órdenes" (RF-07) ----------------------------------------


def test_el_mecanico_solo_edita_diagnostico_y_trabajo(abrir_orden, como):
    orden = abrir_orden()
    mecanico = como(MECANICO)
    ruta = f"/api/v1/ordenes/{orden['id']}"

    assert mecanico.patch(ruta, json={"diagnostico": "Buje"}).status_code == 200
    assert mecanico.patch(ruta, json={"kilometraje": 1}).status_code == 403


def test_reasignar_registra_cada_asignacion(abrir_orden, como, equipo):
    orden = abrir_orden()
    ruta = f"/api/v1/ordenes/{orden['id']}/asignaciones"
    recepcion = como(RECEPCION)

    repetida = recepcion.post(ruta, json={"mecanico_id": equipo["mecanico"].id})
    reasignada = recepcion.post(ruta, json={"mecanico_id": equipo["otro"].id, "nota": "Turno"})

    assert repetida.status_code == 422
    assert reasignada.status_code == 201
    cuerpo = reasignada.json()
    assert cuerpo["mecanico"]["id"] == equipo["otro"].id
    assert [a["mecanico"]["id"] for a in cuerpo["asignaciones"]] == [
        equipo["mecanico"].id,
        equipo["otro"].id,
    ]
    assert len(cuerpo["historial"]) == 1  # reasignar no cambia el estado
    # El mecánico anterior deja de ver la orden; el nuevo la ve.
    assert como(MECANICO).get(f"/api/v1/ordenes/{orden['id']}").status_code == 404
    assert como(OTRO_MECANICO).get(f"/api/v1/ordenes/{orden['id']}").status_code == 200


def test_el_mecanico_no_reasigna(abrir_orden, como, equipo):
    orden = abrir_orden()
    respuesta = como(MECANICO).post(
        f"/api/v1/ordenes/{orden['id']}/asignaciones", json={"mecanico_id": equipo["otro"].id}
    )
    assert respuesta.status_code == 403


def test_mis_ordenes_muestra_solo_las_asignadas(abrir_orden, como, ana, crear_vehiculo, equipo):
    propia = abrir_orden()
    ajena = abrir_orden(vehiculo=crear_vehiculo(ana, "XYZ987"), con_mecanico=False)

    mias = como(MECANICO).get("/api/v1/ordenes", params={"abiertas": True}).json()["data"]
    # Aunque pida las de otro mecánico, el filtro de su rol se mantiene.
    forzado = (
        como(MECANICO)
        .get("/api/v1/ordenes", params={"mecanico_id": equipo["otro"].id})
        .json()["data"]
    )
    todas = como(RECEPCION).get("/api/v1/ordenes").json()["data"]

    assert [o["id"] for o in mias] == [propia["id"]]
    assert forzado == []
    assert {o["id"] for o in todas} == {propia["id"], ajena["id"]}
    assert como(MECANICO).get(f"/api/v1/ordenes/{ajena['id']}").status_code == 404


def test_lista_de_mecanicos_con_su_carga(abrir_orden, como, equipo):
    abrir_orden()
    mecanicos = como(RECEPCION).get("/api/v1/mecanicos").json()
    carga = {m["nombre"]: m["ordenes_abiertas"] for m in mecanicos}
    assert carga == {"Mecanico": 1, "Otro.Mecanico": 0}
    assert como(MECANICO).get("/api/v1/mecanicos").status_code == 403


def test_rn16_no_se_desactiva_un_mecanico_con_ordenes_abiertas(abrir_orden, como, equipo):
    orden = abrir_orden()
    admin = como(ADMIN)
    ruta = f"/api/v1/usuarios/{equipo['mecanico'].id}"

    assert admin.patch(ruta, json={"activo": False}).status_code == 409
    assert admin.patch(ruta, json={"rol": "RECEPCION"}).status_code == 409
    admin.post(
        f"/api/v1/ordenes/{orden['id']}/asignaciones", json={"mecanico_id": equipo["otro"].id}
    )
    assert admin.patch(ruta, json={"activo": False}).status_code == 200


# --- Historial del vehículo (RF-11) ------------------------------------------------------


def test_historial_del_vehiculo(abrir_orden, como, carro):
    primera = abrir_orden()
    cambiar(como(ADMIN), primera, "CANCELADA", "No vino")
    segunda = abrir_orden()

    datos = como(RECEPCION).get("/api/v1/ordenes", params={"vehiculo_id": carro.id}).json()

    assert [o["id"] for o in datos["data"]] == [segunda["id"], primera["id"]]


# --- Aislamiento entre talleres (ADR-006) ------------------------------------------------


def test_aislamiento_orden_de_otro_taller(
    abrir_orden, como, taller_b, crear_usuario, crear_cliente, crear_vehiculo
):
    orden = abrir_orden()
    crear_usuario(taller_b, "admin@b.co")
    mecanico_b = crear_usuario(taller_b, "mecanico@b.co", rol=RolUsuario.MECANICO)
    carro_b = crear_vehiculo(crear_cliente(taller_b), "QWE123")
    ajeno = como("admin@b.co")
    ruta = f"/api/v1/ordenes/{orden['id']}"

    assert ajeno.get(ruta).status_code == 404
    assert ajeno.patch(ruta, json={"diagnostico": "x"}).status_code == 404
    assert cambiar(ajeno, orden, "CANCELADA", "x").status_code == 404
    assert (
        ajeno.post(f"{ruta}/asignaciones", json={"mecanico_id": mecanico_b.id}).status_code == 404
    )
    assert ajeno.get("/api/v1/ordenes").json()["data"] == []
    # Tampoco puede abrir una orden con un carro de A ni asignar un mecánico de A.
    otro_carro = ajeno.post(
        "/api/v1/ordenes", json={"vehiculo_id": orden["vehiculo"]["id"], "motivo_ingreso": "x y"}
    )
    mecanico_ajeno = ajeno.post(
        "/api/v1/ordenes",
        json={
            "vehiculo_id": carro_b.id,
            "motivo_ingreso": "Frenos",
            "mecanico_id": orden["mecanico"]["id"],
        },
    )
    assert otro_carro.status_code == 404
    assert mecanico_ajeno.status_code == 404
