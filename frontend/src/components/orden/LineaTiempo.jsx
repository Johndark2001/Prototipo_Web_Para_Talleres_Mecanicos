import { ESTADOS_ORDEN } from '../../constantes.js'
import { formatearFechaHora } from '../../formato.js'
import Icono from '../Icono.jsx'

const FLUJO = ['RECIBIDO', 'EN_DIAGNOSTICO', 'ESPERANDO_REPUESTOS', 'REPARADO', 'ENTREGADO']

/**
 * Etapas de la orden con la hora en que entró a cada una. ESPERANDO_REPUESTOS es opcional
 * (H-1): solo aparece si la orden pasó o está por esa etapa.
 */
export default function LineaTiempo({ estado, historial }) {
  const ultimaEntrada = {}
  for (const registro of historial) ultimaEntrada[registro.estado_nuevo] = registro.fecha

  const visitado = (e) => e in ultimaEntrada
  const etapas = FLUJO.filter((e) => e !== 'ESPERANDO_REPUESTOS' || visitado(e))
  const indiceActual = etapas.indexOf(estado)
  const cancelada = estado === 'CANCELADA'

  return (
    <ol aria-label="Etapas de la orden" className="flex flex-col gap-2 sm:flex-row sm:gap-0">
      {etapas.map((etapa, indice) => {
        const hecha = cancelada ? visitado(etapa) : indice < indiceActual
        const actual = indice === indiceActual
        const marca = actual
          ? 'border-primario bg-primario text-white'
          : hecha
            ? 'border-exito bg-exito-suave text-exito'
            : 'border-borde bg-superficie text-texto-suave'
        return (
          <li
            key={etapa}
            aria-current={actual ? 'step' : undefined}
            className="flex items-center gap-2 sm:flex-1 sm:flex-col sm:text-center"
          >
            <span className={`flex size-7 shrink-0 items-center justify-center rounded-full border-2 ${marca}`}>
              <Icono nombre={hecha ? 'check' : ESTADOS_ORDEN[etapa].icono} className="size-3.5" />
            </span>
            <span className="text-sm">
              <span className={actual ? 'font-semibold' : ''}>{ESTADOS_ORDEN[etapa].etiqueta}</span>
              {(hecha || actual) && ultimaEntrada[etapa] && (
                <span className="block text-xs text-texto-suave">
                  {formatearFechaHora(ultimaEntrada[etapa])}
                </span>
              )}
              <span className="sr-only">{actual ? ' (etapa actual)' : hecha ? ' (completada)' : ' (pendiente)'}</span>
            </span>
          </li>
        )
      })}
      {cancelada && (
        <li aria-current="step" className="flex items-center gap-2 sm:flex-1 sm:flex-col sm:text-center">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-full border-2 border-peligro bg-peligro-suave text-peligro">
            <Icono nombre="cerrar" className="size-3.5" />
          </span>
          <span className="text-sm font-semibold">
            Cancelada
            <span className="block text-xs font-normal text-texto-suave">
              {formatearFechaHora(ultimaEntrada.CANCELADA)}
            </span>
          </span>
        </li>
      )}
    </ol>
  )
}
