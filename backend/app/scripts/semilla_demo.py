"""Carga datos FICTICIOS de demostración (H-5): dos talleres con usuarios, clientes, carros,
repuestos y órdenes en distintos estados, con mano de obra y repuestos.

Uso, desde la carpeta backend/:
    uv run python -m app.scripts.semilla_demo

Sirve para probar los roles y que un taller no vea los datos del otro. Ambos talleres
tienen un carro con la placa ABC123 a propósito: cada uno debe ver solo el suyo.
Las órdenes, los repuestos y sus líneas se crean con los mismos servicios que usa la API,
así que respetan las reglas de §6 y §7 (el stock baja, quedan los movimientos).
Se puede ejecutar varias veces: lo que ya existe se omite. En una base que ya tenía las
órdenes de demostración, completa con líneas las que sigan abiertas y no tengan ninguna.
Se niega a ejecutarse con ENTORNO=produccion.
"""

import os
import sys
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import obtener_configuracion
from app.core.db import SesionLocal
from app.core.seguridad import hashear_clave
from app.models import (
    Cliente,
    EstadoOrden,
    OrdenTrabajo,
    Repuesto,
    RolUsuario,
    Taller,
    TipoVehiculo,
    Usuario,
    Vehiculo,
)
from app.schemas.inventario import RepuestoCrear
from app.schemas.ordenes import (
    CambioEstado,
    LineaRepuestoCrear,
    LineaServicioCrear,
    OrdenActualizar,
    OrdenCrear,
)
from app.services import inventario as servicio_inventario
from app.services import lineas_orden
from app.services import ordenes as servicio_ordenes

CLAVE_DEMO = os.environ.get("CLAVE_DEMO", "demo12345")

TALLERES = [
    {
        "nombre": "Taller Demo Norte",
        "es_formal": True,
        "usuarios": [
            ("Admin Norte", "admin@norte.demo.co", RolUsuario.ADMIN),
            ("Recepción Norte", "recepcion@norte.demo.co", RolUsuario.RECEPCION),
            ("Mecánico Norte", "mecanico@norte.demo.co", RolUsuario.MECANICO),
        ],
        # (nombre, teléfono, documento, [(placa, marca, modelo, año, color[, tipo])])
        # Sin tipo, el vehículo es un carro.
        "clientes": [
            (
                "Ana Gómez (demo)",
                "3001234567",
                "1000000001",
                [
                    ("ABC123", "Mazda", "3", 2015, "Rojo"),
                    ("JKL45D", "Yamaha", "FZ 2.0", 2019, "Negro", TipoVehiculo.MOTO),
                ],
            ),
            (
                "Pedro Ruiz (demo)",
                "3159876543",
                None,
                [
                    ("XYZ987", "Chevrolet", "Spark GT", 2012, "Gris"),
                ],
            ),
            ("Lucía Torres (demo)", "3205550101", "1000000003", []),
        ],
        # (código, nombre, unidad, precio, stock inicial, stock mínimo). Hay uno bajo el
        # mínimo y uno agotado a propósito, para que se vean las alertas (RF-10).
        "repuestos": [
            ("W712", "Filtro de aceite Mann W712", "unidad", "25000", "2", "3"),
            ("ACE20W50", "Aceite 20W-50 mineral", "litro", "32000", "20", "8"),
            ("PAS-DEL", "Pastillas de freno delanteras", "juego", "85000", "0", "1"),
            ("BUJ-TIJ", "Buje de tijera", "unidad", "35000", "6", "2"),
            ("BUJIA-NGK", "Bujía NGK", "unidad", "18000", "12", "4"),
        ],
        # (placa, motivo, km, ¿con mecánico?, trabajo realizado, estados por los que pasa,
        #  líneas). Línea: ("servicio", descripción, precio) o ("repuesto", código, cantidad).
        "ordenes": [
            (
                "XYZ987",
                "Alineación y balanceo",
                118000,
                True,
                "Alineación y balanceo",
                ["EN_DIAGNOSTICO", "REPARADO", "ENTREGADO"],
                [("servicio", "Alineación y balanceo", "60000")],
            ),
            (
                "ABC123",
                "Ruido en la suspensión delantera",
                48900,
                True,
                None,
                ["EN_DIAGNOSTICO"],
                [
                    ("servicio", "Revisión de suspensión delantera", "40000"),
                    ("repuesto", "BUJ-TIJ", "2"),
                ],
            ),
            ("XYZ987", "Cambio de aceite y filtro", 120500, False, None, [], []),
            (
                "JKL45D",
                "Revisión de frenos",
                15300,
                True,
                None,
                ["EN_DIAGNOSTICO", "ESPERANDO_REPUESTOS"],
                [("servicio", "Revisión de frenos", "30000")],
            ),
        ],
    },
    {
        "nombre": "Taller Demo Chipichape",
        "es_formal": False,
        "usuarios": [
            ("Admin Chipichape", "admin@chipichape.demo.co", RolUsuario.ADMIN),
            ("Mecánico Chipichape", "mecanico@chipichape.demo.co", RolUsuario.MECANICO),
        ],
        "clientes": [
            (
                "Carlos Díaz (demo)",
                "3117778899",
                None,
                [
                    ("ABC123", "Renault", "Logan", 2018, "Blanco"),
                ],
            ),
        ],
        # El mismo código W712 que en el otro taller: cada taller tiene su propio catálogo.
        "repuestos": [
            ("BAT-12V", "Batería 12V 45Ah", "unidad", "320000", "1", "1"),
            ("W712", "Filtro de aceite genérico", "unidad", "18000", "10", "2"),
        ],
        "ordenes": [
            (
                "ABC123",
                "No enciende en las mañanas",
                80200,
                True,
                None,
                [],
                [("servicio", "Diagnóstico del sistema eléctrico", "50000")],
            ),
        ],
    },
]


def cargar_clientes(db: Session, taller_id: int, clientes: list) -> None:
    if db.scalar(select(Cliente.id).where(Cliente.taller_id == taller_id)) is not None:
        print("  Ya tiene clientes; se omiten.")
        return
    for nombre, telefono, documento, vehiculos in clientes:
        cliente = Cliente(
            taller_id=taller_id,
            nombre=nombre,
            telefono=telefono,
            documento=documento,
            autoriza_datos=True,
            fecha_autorizacion=datetime.now(UTC),
        )
        db.add(cliente)
        for placa, marca, modelo, anio, color, *tipo in vehiculos:
            cliente.vehiculos.append(
                Vehiculo(
                    taller_id=taller_id,
                    placa=placa,
                    tipo=tipo[0] if tipo else TipoVehiculo.CARRO,
                    marca=marca,
                    modelo=modelo,
                    anio=anio,
                    color=color,
                )
            )
    print(f"  Creados {len(clientes)} clientes con sus vehículos.")


def _usuario(db: Session, taller_id: int, rol: RolUsuario) -> Usuario:
    return db.scalar(
        select(Usuario).where(Usuario.taller_id == taller_id, Usuario.rol == rol).limit(1)
    )


def cargar_repuestos(db: Session, taller_id: int, repuestos: list) -> None:
    if db.scalar(select(Repuesto.id).where(Repuesto.taller_id == taller_id)) is not None:
        print("  Ya tiene repuestos; se omiten.")
        return
    admin = _usuario(db, taller_id, RolUsuario.ADMIN)
    for codigo, nombre, unidad, precio, stock, minimo in repuestos:
        # Con el servicio de la API: el stock inicial queda como movimiento ENTRADA.
        servicio_inventario.crear(
            db,
            admin,
            RepuestoCrear(
                codigo=codigo,
                nombre=nombre,
                unidad=unidad,
                precio_venta=Decimal(precio),
                stock_inicial=Decimal(stock),
                stock_minimo=Decimal(minimo),
            ),
        )
    print(f"  Creados {len(repuestos)} repuestos.")


def aplicar_lineas(db: Session, actor: Usuario, orden_id: int, lineas: list) -> None:
    for tipo, referencia, valor in lineas:
        if tipo == "servicio":
            lineas_orden.agregar_servicio(
                db,
                actor,
                orden_id,
                LineaServicioCrear(descripcion=referencia, precio_unitario=Decimal(valor)),
            )
        else:
            repuesto_id = db.scalar(
                select(Repuesto.id).where(
                    Repuesto.taller_id == actor.taller_id, Repuesto.codigo == referencia
                )
            )
            lineas_orden.agregar_repuesto(
                db,
                actor,
                orden_id,
                LineaRepuestoCrear(repuesto_id=repuesto_id, cantidad=Decimal(valor)),
            )


def _orden_de_demo(db: Session, taller_id: int, placa: str, motivo: str) -> OrdenTrabajo | None:
    return db.scalar(
        select(OrdenTrabajo)
        .join(Vehiculo, OrdenTrabajo.vehiculo_id == Vehiculo.id)
        .where(
            OrdenTrabajo.taller_id == taller_id,
            Vehiculo.placa == placa,
            OrdenTrabajo.motivo_ingreso == motivo,
        )
    )


def completar_lineas(db: Session, taller_id: int, ordenes: list) -> None:
    """Para bases cargadas antes de la Semana 4: agrega las líneas que faltan."""
    admin = _usuario(db, taller_id, RolUsuario.ADMIN)
    completadas = 0
    for placa, motivo, *_, lineas in ordenes:
        orden = _orden_de_demo(db, taller_id, placa, motivo)
        if not lineas or orden is None or not orden.abierta:
            continue  # RN-07: una orden entregada o cancelada ya no se modifica
        if orden.servicios or orden.repuestos:
            continue
        aplicar_lineas(db, admin, orden.id, lineas)
        completadas += 1
    print(f"  Órdenes abiertas completadas con mano de obra y repuestos: {completadas}.")


def cargar_ordenes(db: Session, taller_id: int, ordenes: list) -> None:
    if db.scalar(select(OrdenTrabajo.id).where(OrdenTrabajo.taller_id == taller_id)):
        print("  Ya tiene órdenes; se omiten.")
        completar_lineas(db, taller_id, ordenes)
        return
    admin = _usuario(db, taller_id, RolUsuario.ADMIN)
    mecanico = _usuario(db, taller_id, RolUsuario.MECANICO)
    for placa, motivo, km, con_mecanico, trabajo, estados, lineas in ordenes:
        vehiculo_id = db.scalar(
            select(Vehiculo.id).where(Vehiculo.taller_id == taller_id, Vehiculo.placa == placa)
        )
        orden = servicio_ordenes.crear(
            db,
            admin,
            OrdenCrear(
                vehiculo_id=vehiculo_id,
                motivo_ingreso=motivo,
                kilometraje=km,
                mecanico_id=mecanico.id if con_mecanico else None,
            ),
        )
        # Las líneas van antes de los cambios de estado: después de entregar ya no se puede.
        aplicar_lineas(db, admin, orden.id, lineas)
        for estado in estados:
            # El mecánico hace los cambios de taller; el ADMIN entrega.
            actor = admin if estado == EstadoOrden.ENTREGADO else mecanico
            if estado == EstadoOrden.REPARADO:
                servicio_ordenes.actualizar(
                    db, actor, orden.id, OrdenActualizar(trabajo_realizado=trabajo)
                )
            nota = "Falta el repuesto" if estado == EstadoOrden.ESPERANDO_REPUESTOS else None
            servicio_ordenes.cambiar_estado(
                db, actor, orden.id, CambioEstado(estado=estado, nota=nota)
            )
    print(f"  Creadas {len(ordenes)} órdenes.")


def main() -> None:
    if obtener_configuracion().es_produccion:
        sys.exit("La semilla de demostración no se ejecuta en producción.")

    hash_demo = hashear_clave(CLAVE_DEMO)
    with SesionLocal() as db:
        for datos in TALLERES:
            correos = [email for _, email, _ in datos["usuarios"]]
            existente = db.scalar(select(Usuario.taller_id).where(Usuario.email.in_(correos)))
            if existente is not None:
                print(f"'{datos['nombre']}' ya existe; se omiten sus usuarios.")
                cargar_clientes(db, existente, datos["clientes"])
                continue
            taller = Taller(nombre=datos["nombre"], es_formal=datos["es_formal"])
            db.add(taller)
            db.flush()
            for nombre, email, rol in datos["usuarios"]:
                db.add(
                    Usuario(
                        taller_id=taller.id,
                        nombre=nombre,
                        email=email,
                        password_hash=hash_demo,
                        rol=rol,
                    )
                )
            print(f"Creado '{taller.nombre}' con {len(datos['usuarios'])} usuarios.")
            cargar_clientes(db, taller.id, datos["clientes"])
        db.commit()
        for datos in TALLERES:
            correo_admin = datos["usuarios"][0][1]
            taller_id = db.scalar(select(Usuario.taller_id).where(Usuario.email == correo_admin))
            print(f"Inventario y órdenes de '{datos['nombre']}':")
            cargar_repuestos(db, taller_id, datos["repuestos"])
            cargar_ordenes(db, taller_id, datos["ordenes"])
    print(f"Clave de todos los usuarios de demostración: {CLAVE_DEMO}")


if __name__ == "__main__":
    main()
