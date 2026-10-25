"""Carga datos FICTICIOS de demostración (H-5): dos talleres con usuarios, clientes, carros
y órdenes en distintos estados.

Uso, desde la carpeta backend/:
    uv run python -m app.scripts.semilla_demo

Sirve para probar los roles y que un taller no vea los datos del otro. Ambos talleres
tienen un carro con la placa ABC123 a propósito: cada uno debe ver solo el suyo.
Las órdenes se crean con los mismos servicios que usa la API, así que respetan las reglas
de §7. Se puede ejecutar varias veces: lo que ya existe se omite.
Se niega a ejecutarse con ENTORNO=produccion.
"""

import os
import sys
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import obtener_configuracion
from app.core.db import SesionLocal
from app.core.seguridad import hashear_clave
from app.models import Cliente, EstadoOrden, OrdenTrabajo, RolUsuario, Taller, Usuario, Vehiculo
from app.schemas.ordenes import CambioEstado, OrdenActualizar, OrdenCrear
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
        # (nombre, teléfono, documento, [(placa, marca, modelo, año, color)])
        "clientes": [
            (
                "Ana Gómez (demo)",
                "3001234567",
                "1000000001",
                [
                    ("ABC123", "Mazda", "3", 2015, "Rojo"),
                    ("JKL45D", "Yamaha", "FZ 2.0", 2019, "Negro"),
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
        # (placa, motivo, km, ¿con mecánico?, trabajo realizado, estados por los que pasa)
        "ordenes": [
            (
                "XYZ987",
                "Alineación y balanceo",
                118000,
                True,
                "Alineación y balanceo",
                ["EN_DIAGNOSTICO", "REPARADO", "ENTREGADO"],
            ),
            ("ABC123", "Ruido en la suspensión delantera", 48900, True, None, ["EN_DIAGNOSTICO"]),
            ("XYZ987", "Cambio de aceite y filtro", 120500, False, None, []),
            (
                "JKL45D",
                "Revisión de frenos",
                15300,
                True,
                None,
                ["EN_DIAGNOSTICO", "ESPERANDO_REPUESTOS"],
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
        "ordenes": [
            ("ABC123", "No enciende en las mañanas", 80200, True, None, []),
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
        for placa, marca, modelo, anio, color in vehiculos:
            cliente.vehiculos.append(
                Vehiculo(
                    taller_id=taller_id,
                    placa=placa,
                    marca=marca,
                    modelo=modelo,
                    anio=anio,
                    color=color,
                )
            )
    print(f"  Creados {len(clientes)} clientes con sus carros.")


def _usuario(db: Session, taller_id: int, rol: RolUsuario) -> Usuario:
    return db.scalar(
        select(Usuario).where(Usuario.taller_id == taller_id, Usuario.rol == rol).limit(1)
    )


def cargar_ordenes(db: Session, taller_id: int, ordenes: list) -> None:
    if db.scalar(select(OrdenTrabajo.id).where(OrdenTrabajo.taller_id == taller_id)):
        print("  Ya tiene órdenes; se omiten.")
        return
    admin = _usuario(db, taller_id, RolUsuario.ADMIN)
    mecanico = _usuario(db, taller_id, RolUsuario.MECANICO)
    for placa, motivo, km, con_mecanico, trabajo, estados in ordenes:
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
            print(f"Órdenes de '{datos['nombre']}':")
            cargar_ordenes(db, taller_id, datos["ordenes"])
    print(f"Clave de todos los usuarios de demostración: {CLAVE_DEMO}")


if __name__ == "__main__":
    main()
