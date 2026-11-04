"""Catálogo de categorías del problema con que entra un vehículo (cambio #5).

Lo registran ADMIN y RECEPCION al abrir la orden, nunca el cliente ni el mecánico. La lista
depende del tipo de vehículo: una moto no tiene "Aire acondicionado" ni un carro "Kit de
arrastre". Se guarda el nombre (no un código) para que la orden y su informe PDF sigan
diciendo lo mismo aunque el catálogo cambie después.
"""

import unicodedata

from app.core.errores import DatosInvalidos
from app.models import TipoVehiculo

OTRO = "Otro"

CATEGORIAS: dict[TipoVehiculo, tuple[str, ...]] = {
    TipoVehiculo.CARRO: (
        "Cambio de aceite",
        "Cambio de filtros",
        "Problemas de frenos",
        "Problemas de motor",
        "Sobrecalentamiento",
        "Problemas eléctricos",
        "Problemas de batería",
        "Problemas de arranque",
        "Problemas de suspensión",
        "Problemas de dirección",
        "Problemas de transmisión",
        "Problemas de embrague",
        "Cambio de llantas",
        "Alineación y balanceo",
        "Aire acondicionado",
        "Sistema de refrigeración",
        "Sistema de escape",
        "Inyección electrónica",
        "Problemas de iluminación",
        "Mantenimiento preventivo de carro",
        "Revisión general de carro",
        OTRO,
    ),
    TipoVehiculo.MOTO: (
        "Cambio de aceite",
        "Cambio de filtros",
        "Problemas de frenos",
        "Problemas de motor",
        "Problemas eléctricos",
        "Problemas de batería",
        "Problemas de arranque",
        "Problemas de suspensión",
        "Problemas de transmisión",
        "Cadena de transmisión",
        "Kit de arrastre",
        "Sistema de encendido",
        "Problemas de carburación",
        "Problemas de inyección",
        "Problemas de iluminación",
        "Cambio de llantas",
        "Problemas de embrague",
        "Mantenimiento preventivo de motocicleta",
        "Revisión general de motocicleta",
        OTRO,
    ),
}


def _clave(texto: str) -> str:
    """Sin tildes ni mayúsculas: "BATERIA" y "batería" son la misma búsqueda."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").casefold().strip()


def buscar(tipo: TipoVehiculo, texto: str = "") -> list[str]:
    """Coincidencia parcial sin tildes ("fren" → "Problemas de frenos")."""
    consulta = _clave(texto)
    return [c for c in CATEGORIAS[tipo] if consulta in _clave(c)]


def validar(tipo: TipoVehiculo, categoria: str, otro: str | None) -> tuple[str, str | None]:
    """Devuelve la categoría tal como está en el catálogo y el detalle de "Otro" (o None)."""
    encontrada = next((c for c in CATEGORIAS[tipo] if _clave(c) == _clave(categoria)), None)
    if encontrada is None:
        nombre = "la moto" if tipo == TipoVehiculo.MOTO else "el carro"
        raise DatosInvalidos("categoria_problema", f"Elija una categoría de la lista para {nombre}")
    if encontrada != OTRO:
        return encontrada, None
    if not otro or len(otro.strip()) < 3:
        raise DatosInvalidos("categoria_otro", "Describa el problema (al menos 3 caracteres)")
    return encontrada, otro.strip()


def nombre_problema(categoria: str | None, otro: str | None) -> str | None:
    """Lo que se muestra: el detalle escrito cuando la categoría es "Otro"."""
    if categoria == OTRO and otro:
        return f"{OTRO}: {otro}"
    return categoria


def componer_motivo(categoria: str, otro: str | None, observacion: str | None) -> str:
    """Texto de `motivo_ingreso` (columna obligatoria desde la migración 0003).

    Se sigue llenando para que las listas, el dashboard y cualquier consulta anterior al
    catálogo sigan mostrando por qué entró el vehículo.
    """
    problema = nombre_problema(categoria, otro) or categoria
    return f"{problema} — {observacion}" if observacion else problema
