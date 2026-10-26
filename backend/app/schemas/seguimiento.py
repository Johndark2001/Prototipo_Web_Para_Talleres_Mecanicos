"""Respuesta pública del seguimiento (RF-13). Solo lo que permite ADR-005: si un campo no está
declarado aquí, no sale. No hay datos del cliente, notas internas ni nombres de usuarios."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models import EstadoOrden
from app.schemas.ordenes import Liquidacion


class EtapaPublica(BaseModel):
    estado: EstadoOrden
    fecha: datetime


class ServicioPublico(BaseModel):
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal


class RepuestoPublico(BaseModel):
    nombre: str
    unidad: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal


class SeguimientoSalida(BaseModel):
    taller: str
    numero: int
    placa: str  # enmascarada: ABC***
    marca: str
    modelo: str
    estado: EstadoOrden
    etapas: list[EtapaPublica]
    servicios: list[ServicioPublico]
    repuestos: list[RepuestoPublico]
    liquidacion: Liquidacion
