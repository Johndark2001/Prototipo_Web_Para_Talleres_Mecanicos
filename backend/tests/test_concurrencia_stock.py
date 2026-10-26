"""RN-02 con solicitudes simultáneas: cada hilo usa su propia conexión, como dos personas
registrando el mismo repuesto a la vez en órdenes distintas."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from app.core.db import SesionLocal
from app.core.errores import Conflicto
from app.models import MovimientoInventario, Repuesto, RolUsuario, Usuario
from app.schemas.ordenes import LineaRepuestoCrear, OrdenCrear
from app.services import lineas_orden
from app.services import ordenes as servicio_ordenes

HILOS = 6
STOCK = 4


def test_rn02_repuestos_simultaneos_nunca_dejan_el_stock_negativo(
    db, taller_a, crear_usuario, crear_cliente, crear_vehiculo, crear_repuesto
):
    recepcion = crear_usuario(taller_a, "recepcion@a.co", rol=RolUsuario.RECEPCION)
    ana = crear_cliente(taller_a)
    ordenes = [
        servicio_ordenes.crear(
            db,
            recepcion,
            OrdenCrear(
                vehiculo_id=crear_vehiculo(ana, f"AAA{i:03d}").id, motivo_ingreso="Revisión"
            ),
        ).id
        for i in range(HILOS)
    ]
    repuesto = crear_repuesto(taller_a, "W712", stock_actual=str(STOCK))
    barrera = Barrier(HILOS)

    def agregar(orden_id: int):
        with SesionLocal() as sesion:
            actual = sesion.get(Usuario, recepcion.id)
            barrera.wait()  # todos piden el repuesto al mismo tiempo
            try:
                lineas_orden.agregar_repuesto(
                    sesion,
                    actual,
                    orden_id,
                    LineaRepuestoCrear(repuesto_id=repuesto.id, cantidad=Decimal(1)),
                )
                return True
            except Conflicto:
                return False

    with ThreadPoolExecutor(max_workers=HILOS) as grupo:
        resultados = list(grupo.map(agregar, ordenes))

    db.expire_all()
    assert resultados.count(True) == STOCK
    assert resultados.count(False) == HILOS - STOCK
    assert db.get(Repuesto, repuesto.id).stock_actual == 0
    # Cada salida dejó un stock resultante distinto: nadie partió de un stock viejo.
    resultantes = sorted(m.stock_resultante for m in db.query(MovimientoInventario).all())
    assert resultantes == [Decimal(n) for n in range(STOCK)]
