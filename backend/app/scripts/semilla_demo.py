"""Carga datos FICTICIOS de demostración (H-5): dos talleres con un usuario por rol.

Uso, desde la carpeta backend/:
    uv run python -m app.scripts.semilla_demo

Sirve para probar los roles y que un taller no vea los datos del otro.
Se niega a ejecutarse con ENTORNO=produccion.
"""

import os
import sys

from sqlalchemy import select

from app.core.config import obtener_configuracion
from app.core.db import SesionLocal
from app.core.seguridad import hashear_clave
from app.models import RolUsuario, Taller, Usuario

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
    },
    {
        "nombre": "Taller Demo Chipichape",
        "es_formal": False,
        "usuarios": [
            ("Admin Chipichape", "admin@chipichape.demo.co", RolUsuario.ADMIN),
            ("Mecánico Chipichape", "mecanico@chipichape.demo.co", RolUsuario.MECANICO),
        ],
    },
]


def main() -> None:
    if obtener_configuracion().es_produccion:
        sys.exit("La semilla de demostración no se ejecuta en producción.")

    hash_demo = hashear_clave(CLAVE_DEMO)
    with SesionLocal() as db:
        for datos in TALLERES:
            correos = [email for _, email, _ in datos["usuarios"]]
            if db.scalar(select(Usuario.id).where(Usuario.email.in_(correos))) is not None:
                print(f"'{datos['nombre']}' ya existe; se omite.")
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
        db.commit()
    print(f"Clave de todos los usuarios de demostración: {CLAVE_DEMO}")


if __name__ == "__main__":
    main()
