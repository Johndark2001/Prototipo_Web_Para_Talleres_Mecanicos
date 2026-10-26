from fastapi import APIRouter, Request

from app.api.deps import DB
from app.core.errores import DemasiadasSolicitudes
from app.core.limites import LimitadorSolicitudes
from app.schemas.seguimiento import (
    EtapaPublica,
    RepuestoPublico,
    SeguimientoSalida,
    ServicioPublico,
)
from app.services import liquidacion
from app.services import seguimiento as servicio

router = APIRouter(prefix="/seguimiento", tags=["seguimiento público"])

# Un cliente revisa su orden unas pocas veces; 30 por minuto y por IP frena a quien pruebe
# códigos al azar sin molestar a nadie (SPEC §10, ADR-005).
limitador = LimitadorSolicitudes(maximo=30, ventana_segundos=60)


@router.get("/{codigo}", response_model=SeguimientoSalida)
def ver_seguimiento(codigo: str, request: Request, db: DB) -> SeguimientoSalida:
    """Sin sesión: el código aleatorio del enlace es la única llave."""
    if not limitador.permitir(request.client.host if request.client else "desconocido"):
        raise DemasiadasSolicitudes("Demasiadas consultas seguidas. Espere un minuto.")

    orden = servicio.obtener_por_codigo(db, codigo)
    return SeguimientoSalida(
        taller=orden.taller.nombre,
        numero=orden.numero,
        placa=servicio.enmascarar_placa(orden.vehiculo.placa),
        marca=orden.vehiculo.marca,
        modelo=orden.vehiculo.modelo,
        estado=orden.estado,
        etapas=[EtapaPublica(estado=h.estado_nuevo, fecha=h.fecha) for h in orden.historial],
        servicios=[
            ServicioPublico(
                descripcion=s.descripcion,
                cantidad=s.cantidad,
                precio_unitario=s.precio_unitario,
                subtotal=s.subtotal,
            )
            for s in orden.servicios
        ],
        repuestos=[
            RepuestoPublico(
                nombre=r.repuesto.nombre,
                unidad=r.repuesto.unidad,
                cantidad=r.cantidad,
                precio_unitario=r.precio_unitario,
                subtotal=r.subtotal,
            )
            for r in orden.repuestos
        ],
        liquidacion=liquidacion.calcular(orden),
    )
