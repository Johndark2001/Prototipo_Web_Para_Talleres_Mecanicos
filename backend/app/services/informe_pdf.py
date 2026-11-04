"""Informe PDF final para el cliente (cambio #4B).

Solo existe cuando la orden fue ENTREGADA: antes los valores todavía pueden cambiar y una
orden cancelada no tiene trabajo que informar. Hay dos versiones:

- la del taller (`publico=False`), que incluye nombre y teléfono del cliente y la placa
  completa, para imprimirla o enviarla;
- la del portal de seguimiento (`publico=True`), que respeta ADR-005: quien tenga el enlace
  no ve datos personales, así que el cliente y la placa salen ocultos.

Ninguna incluye notas internas ni nombres de los usuarios del taller. Se usa la fuente
Helvetica del propio PDF (Latin-1): los caracteres fuera de ella se reemplazan.
"""

from datetime import datetime
from decimal import Decimal

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.core.errores import Conflicto
from app.models import EstadoOrden, OrdenTrabajo, TipoVehiculo
from app.services import categorias, liquidacion
from app.services.dashboard import HORA_COLOMBIA
from app.services.seguimiento import enmascarar_placa

NOMBRES_ESTADO = {
    EstadoOrden.RECIBIDO: "Recibido",
    EstadoOrden.EN_DIAGNOSTICO: "En diagnóstico",
    EstadoOrden.ESPERANDO_REPUESTOS: "Esperando repuestos",
    EstadoOrden.REPARADO: "Reparado",
    EstadoOrden.ENTREGADO: "Entregado",
    EstadoOrden.CANCELADA: "Cancelada",
}
REEMPLAZOS = str.maketrans(
    {"—": "-", "–": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "•": "-"}
)
COLOR_TEXTO = (33, 37, 41)
COLOR_SUAVE = (100, 106, 115)
COLOR_LINEA = (210, 214, 220)
COLOR_PRIMARIO = (29, 78, 137)


def exigir_entregada(orden: OrdenTrabajo) -> None:
    if orden.estado != EstadoOrden.ENTREGADO:
        raise Conflicto("El informe PDF solo está disponible cuando la orden fue entregada")


def nombre_archivo(orden: OrdenTrabajo) -> str:
    return f"informe-orden-{orden.numero}.pdf"


def _texto(valor: object) -> str:
    """Latin-1 para la fuente estándar del PDF; lo que no cabe se cambia por "?"."""
    texto = str(valor).translate(REEMPLAZOS)
    return texto.encode("latin-1", "replace").decode("latin-1")


def _pesos(valor: Decimal) -> str:
    """Decimal("143500.50") → "$ 143.500,50"; sin centavos cuando son cero."""
    decimales = 0 if valor == valor.to_integral_value() else 2
    entero = f"{valor:,.{decimales}f}"
    return "$ " + entero.replace(",", "_").replace(".", ",").replace("_", ".")


def _cantidad(valor: Decimal) -> str:
    texto = f"{valor.normalize():f}"
    return texto.replace(".", ",")


def _fecha_hora(valor: datetime) -> str:
    return valor.astimezone(HORA_COLOMBIA).strftime("%d/%m/%Y %I:%M %p").lower()


class _Informe(FPDF):
    def __init__(self, taller: str, numero: int):
        super().__init__(format="Letter")
        self.taller = taller
        self.numero = numero
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_title(_texto(f"Informe de la orden #{numero}"))
        self.set_author(_texto(taller))
        self.set_creator("Taller Digital")

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", size=8)
        self.set_text_color(*COLOR_SUAVE)
        self.cell(0, 5, _texto(f"{self.taller} - Orden #{self.numero}"), align="L")
        self.set_x(self.l_margin)
        self.cell(0, 5, _texto(f"Página {self.page_no()} de {{nb}}"), align="R")

    # --- Bloques -------------------------------------------------------------------------

    def titulo_seccion(self, texto: str) -> None:
        if self.get_y() > self.h - 45:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*COLOR_PRIMARIO)
        self.cell(0, 7, _texto(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*COLOR_LINEA)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_text_color(*COLOR_TEXTO)

    def dato(self, etiqueta: str, valor: str | None) -> None:
        ancho_etiqueta = 52
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*COLOR_SUAVE)
        y = self.get_y()
        self.multi_cell(ancho_etiqueta, 5.5, _texto(etiqueta), new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font("Helvetica", size=10)
        self.set_text_color(*COLOR_TEXTO)
        self.multi_cell(0, 5.5, _texto(valor or "-"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(max(self.get_y(), y + 5.5))
        self.ln(0.8)

    def parrafo(self, texto: str | None, vacio: str = "Sin registro.") -> None:
        self.set_font("Helvetica", size=10)
        if texto and texto.strip():
            self.set_text_color(*COLOR_TEXTO)
            self.multi_cell(0, 5.5, _texto(texto.strip()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.set_text_color(*COLOR_SUAVE)
            self.multi_cell(0, 5.5, _texto(vacio), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*COLOR_TEXTO)

    def tabla(self, encabezados: list[str], anchos: list[float], filas: list[list[str]]) -> None:
        alineaciones = ["L"] + ["R"] * (len(encabezados) - 1)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(240, 242, 245)
        for texto, ancho, alineacion in zip(encabezados, anchos, alineaciones, strict=True):
            self.cell(ancho, 7, _texto(texto), border="B", align=alineacion, fill=True)
        self.ln()
        self.set_font("Helvetica", size=9.5)
        for fila in filas:
            # La descripción puede ocupar varias líneas; las cifras van en la primera.
            lineas = self.multi_cell(anchos[0], 5.5, _texto(fila[0]), dry_run=True, output="LINES")
            alto = 5.5 * max(len(lineas), 1)
            if self.get_y() + alto > self.h - 22:
                self.add_page()
            y = self.get_y()
            self.multi_cell(anchos[0], 5.5, _texto(fila[0]), new_x=XPos.RIGHT, new_y=YPos.TOP)
            x = self.l_margin + anchos[0]
            for texto, ancho in zip(fila[1:], anchos[1:], strict=True):
                self.set_xy(x, y)
                self.cell(ancho, 5.5, _texto(texto), align="R")
                x += ancho
            self.set_xy(self.l_margin, y + alto)
            self.set_draw_color(*COLOR_LINEA)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(0.8)


def generar(orden: OrdenTrabajo, publico: bool = False) -> bytes:
    """PDF del informe final. La orden debe traer taller, vehículo, cliente, historial y líneas."""
    exigir_entregada(orden)
    vehiculo = orden.vehiculo
    total = liquidacion.calcular(orden)
    pdf = _Informe(orden.taller.nombre, orden.numero)
    pdf.add_page()

    # Encabezado
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*COLOR_PRIMARIO)
    pdf.multi_cell(0, 9, _texto(orden.taller.nombre), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(*COLOR_SUAVE)
    pdf.cell(0, 6, "Informe de servicio", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_text_color(*COLOR_TEXTO)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 7, f"Orden #{orden.numero}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.titulo_seccion("Datos de la orden")
    pdf.dato("Fecha de ingreso", _fecha_hora(orden.fecha_ingreso))
    pdf.dato("Fecha de entrega", _fecha_hora(orden.fecha_entrega) if orden.fecha_entrega else None)
    if publico:
        pdf.dato("Cliente", "Datos personales protegidos (Ley 1581 de 2012)")
    else:
        pdf.dato("Cliente", orden.cliente.nombre)
        pdf.dato("Teléfono", orden.cliente.telefono or None)

    tipo = "Moto" if vehiculo.tipo == TipoVehiculo.MOTO else "Carro"
    placa = enmascarar_placa(vehiculo.placa) if publico else vehiculo.placa
    descripcion = " ".join(str(p) for p in (vehiculo.marca, vehiculo.modelo, vehiculo.anio) if p)
    color = f" - {vehiculo.color}" if vehiculo.color else ""
    pdf.dato("Vehículo", f"{tipo} {descripcion}{color}")
    pdf.dato("Placa", placa)
    if orden.kilometraje is not None and not publico:  # el seguimiento público tampoco lo muestra
        pdf.dato("Kilometraje", f"{orden.kilometraje:,} km".replace(",", "."))

    pdf.titulo_seccion("Motivo de ingreso")
    pdf.dato(
        "Categoría del problema",
        categorias.nombre_problema(orden.categoria_problema, orden.categoria_otro)
        or "Sin categoría (orden registrada antes del catálogo)",
    )
    pdf.dato("Observación del cliente", orden.observacion_cliente or orden.motivo_ingreso)

    pdf.titulo_seccion("Diagnóstico")
    pdf.parrafo(orden.diagnostico)

    pdf.titulo_seccion("Trabajo realizado")
    pdf.parrafo(orden.trabajo_realizado)

    pdf.titulo_seccion("Mano de obra")
    if orden.servicios:
        pdf.tabla(
            ["Descripción", "Cantidad", "Valor unitario", "Subtotal"],
            [88, 22, 35, 35],
            [
                [
                    s.descripcion,
                    _cantidad(s.cantidad),
                    _pesos(s.precio_unitario),
                    _pesos(s.subtotal),
                ]
                for s in orden.servicios
            ],
        )
    else:
        pdf.parrafo(None, "No se registró mano de obra.")

    pdf.titulo_seccion("Repuestos")
    if orden.repuestos:
        pdf.tabla(
            ["Repuesto", "Cantidad", "Valor unitario", "Subtotal"],
            [88, 22, 35, 35],
            [
                [
                    r.repuesto.nombre,
                    f"{_cantidad(r.cantidad)} {r.repuesto.unidad}",
                    _pesos(r.precio_unitario),
                    _pesos(r.subtotal),
                ]
                for r in orden.repuestos
            ],
        )
    else:
        pdf.parrafo(None, "No se usaron repuestos.")

    pdf.titulo_seccion("Total")
    for etiqueta, valor, negrita in (
        ("Mano de obra", total["mano_de_obra"], False),
        ("Repuestos", total["repuestos"], False),
        ("Total", total["total"], True),
    ):
        pdf.set_font("Helvetica", "B" if negrita else "", 12 if negrita else 10)
        pdf.cell(145, 7, etiqueta, align="R")
        pdf.cell(35, 7, _texto(_pesos(valor)), align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=8.5)
    pdf.set_text_color(*COLOR_SUAVE)
    pdf.cell(0, 5, "Valores sin IVA.", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*COLOR_TEXTO)

    pdf.titulo_seccion("Historial de estados")
    pdf.tabla(
        ["Estado", "Fecha"],
        [120, 60],
        [[NOMBRES_ESTADO[h.estado_nuevo], _fecha_hora(h.fecha)] for h in orden.historial],
    )

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*COLOR_PRIMARIO)
    pdf.multi_cell(
        0,
        7,
        _texto(f"¡Gracias por confiar en {orden.taller.nombre}!"),
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(*COLOR_SUAVE)
    pdf.multi_cell(
        0,
        5.5,
        "Conserve este informe como constancia del servicio. Fue un gusto atenderle.",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    return bytes(pdf.output())
