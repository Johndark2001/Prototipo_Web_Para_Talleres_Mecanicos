import { ESTADOS_ORDEN } from '../constantes.js'
import Icono from './Icono.jsx'

/** Estado de la orden con ícono y texto (SPEC §11: ChipEstado). */
export default function ChipEstado({ estado }) {
  const { etiqueta, icono, clase } = ESTADOS_ORDEN[estado]
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${clase}`}
    >
      <Icono nombre={icono} className="size-3.5" />
      {etiqueta}
    </span>
  )
}
