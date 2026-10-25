"""Carga datos FICTICIOS de demostración (H-5): dos talleres con usuarios, clientes y carros.

Uso, desde la carpeta backend/:
    uv run python -m app.scripts.semilla_demo

Sirve para probar los roles y que un taller no vea los datos del otro. Ambos talleres
tienen un carro con la placa ABC123 a propósito: cada uno debe ver solo el suyo.
Se puede ejecutar varias veces: lo que ya existe se omite.
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
from app.models import Cliente, RolUsuario, Taller, Usuario, Vehiculo

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
    print(f"Clave de todos los usuarios de demostración: {CLAVE_DEMO}")


if __name__ == "__main__":
    main()
