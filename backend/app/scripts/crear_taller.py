"""Crea un taller y su primer administrador (ADR-006: no hay registro público).

Uso, desde la carpeta backend/:
    uv run python -m app.scripts.crear_taller --taller "Taller Norte" \
        --nombre "Ana Gómez" --email ana@tallernorte.co [--formal]

La clave se pide por teclado (no queda en el historial de la terminal).
Para automatizar, puede pasarse en la variable de entorno CLAVE_ADMIN.
"""

import argparse
import os
import sys
from getpass import getpass

from sqlalchemy import select

from app.core.db import SesionLocal
from app.core.seguridad import hashear_clave
from app.models import RolUsuario, Taller, Usuario

LONGITUD_MINIMA_CLAVE = 8


def pedir_clave() -> str:
    clave = os.environ.get("CLAVE_ADMIN")
    if clave:
        return clave
    clave = getpass("Clave del administrador: ")
    if getpass("Repita la clave: ") != clave:
        sys.exit("Las claves no coinciden.")
    return clave


def main() -> None:
    parser = argparse.ArgumentParser(description="Crea un taller y su administrador")
    parser.add_argument("--taller", required=True, help="Nombre del taller")
    parser.add_argument("--nombre", required=True, help="Nombre del administrador")
    parser.add_argument("--email", required=True, help="Correo del administrador")
    parser.add_argument("--formal", action="store_true", help="El taller tiene registro mercantil")
    args = parser.parse_args()

    email = args.email.strip().lower()
    clave = pedir_clave()
    if len(clave) < LONGITUD_MINIMA_CLAVE:
        sys.exit(f"La clave debe tener al menos {LONGITUD_MINIMA_CLAVE} caracteres.")

    with SesionLocal() as db:
        if db.scalar(select(Usuario.id).where(Usuario.email == email)) is not None:
            sys.exit(f"Ya existe un usuario con el correo {email}.")
        taller = Taller(nombre=args.taller.strip(), es_formal=args.formal)
        db.add(taller)
        db.flush()
        db.add(
            Usuario(
                taller_id=taller.id,
                nombre=args.nombre.strip(),
                email=email,
                password_hash=hashear_clave(clave),
                rol=RolUsuario.ADMIN,
            )
        )
        db.commit()
        print(f"Taller '{taller.nombre}' creado (id {taller.id}). Administrador: {email}")


if __name__ == "__main__":
    main()
