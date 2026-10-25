"""Dos recepciones a la vez: cada hilo usa su propia conexión, como dos solicitudes reales."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app.core.db import SesionLocal
from app.core.errores import Conflicto
from app.models import Usuario
from app.schemas.ordenes import OrdenCrear
from app.services import ordenes as servicio

HILOS = 6


def abrir_en_paralelo(usuario_id: int, vehiculo_ids: list[int]) -> list:
    barrera = Barrier(len(vehiculo_ids))

    def abrir(vehiculo_id: int):
        with SesionLocal() as db:
            actual = db.get(Usuario, usuario_id)
            barrera.wait()  # todos los hilos piden el número al mismo tiempo
            try:
                return servicio.crear(
                    db, actual, OrdenCrear(vehiculo_id=vehiculo_id, motivo_ingreso="Revisión")
                ).numero
            except Conflicto as exc:
                return exc

    with ThreadPoolExecutor(max_workers=len(vehiculo_ids)) as grupo:
        return list(grupo.map(abrir, vehiculo_ids))


def test_rn12_recepciones_simultaneas_reciben_numeros_distintos(
    taller_a, crear_usuario, crear_cliente, crear_vehiculo
):
    recepcion = crear_usuario(taller_a, "recepcion@a.co")
    ana = crear_cliente(taller_a)
    carros = [crear_vehiculo(ana, f"AAA{i:03d}").id for i in range(HILOS)]

    numeros = abrir_en_paralelo(recepcion.id, carros)

    assert sorted(numeros) == list(range(1, HILOS + 1))


def test_rn08_dos_recepciones_del_mismo_carro_solo_abren_una_orden(
    taller_a, crear_usuario, crear_cliente, crear_vehiculo
):
    recepcion = crear_usuario(taller_a, "recepcion@a.co")
    carro = crear_vehiculo(crear_cliente(taller_a), "ABC123")

    resultados = abrir_en_paralelo(recepcion.id, [carro.id] * HILOS)

    abiertas = [r for r in resultados if isinstance(r, int)]
    rechazadas = [r for r in resultados if isinstance(r, Conflicto)]
    assert len(abiertas) == 1
    assert len(rechazadas) == HILOS - 1
