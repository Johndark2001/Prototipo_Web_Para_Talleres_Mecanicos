import { ESTADOS_ORDEN } from '../../constantes.js'
import { formatearFechaHora } from '../../formato.js'

/** Registro de cambios de estado y de asignaciones, del más reciente al más antiguo. */
export default function HistorialOrden({ historial, asignaciones }) {
  const eventos = [
    ...historial.map((h) => ({
      clave: `e${h.id}`,
      fecha: h.fecha,
      quien: h.usuario.nombre,
      texto: h.estado_anterior
        ? `${ESTADOS_ORDEN[h.estado_anterior].etiqueta} → ${ESTADOS_ORDEN[h.estado_nuevo].etiqueta}`
        : 'Abrió la orden',
      nota: h.nota,
    })),
    ...asignaciones.map((a, i) => ({
      clave: `a${a.id}`,
      fecha: a.fecha,
      quien: a.asignador.nombre,
      texto: `${i === 0 ? 'Asignó' : 'Reasignó'} a ${a.mecanico.nombre}`,
      nota: a.nota,
    })),
  ].sort((x, y) => (x.fecha < y.fecha ? 1 : -1))

  return (
    <ol className="flex flex-col divide-y divide-borde rounded-lg border border-borde bg-superficie">
      {eventos.map((evento) => (
        <li key={evento.clave} className="flex flex-col gap-0.5 px-4 py-3 text-sm">
          <p>
            <span className="font-medium">{evento.texto}</span>
            <span className="text-texto-suave"> · {evento.quien}</span>
          </p>
          <p className="text-xs text-texto-suave">{formatearFechaHora(evento.fecha)}</p>
          {evento.nota && <p className="mt-1 rounded bg-fondo px-2 py-1">«{evento.nota}»</p>}
        </li>
      ))}
    </ol>
  )
}
