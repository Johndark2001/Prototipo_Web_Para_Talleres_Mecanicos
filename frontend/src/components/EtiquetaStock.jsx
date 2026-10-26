import { formatearCantidad } from '../formato.js'
import Icono from './Icono.jsx'

/**
 * Stock de un repuesto con su alerta (RN-04, RF-10). El color nunca va solo: el texto dice
 * "Agotado" o "Stock bajo" y lleva ícono (RNF-07).
 */
export default function EtiquetaStock({ repuesto }) {
  const agotado = Number(repuesto.stock_actual) === 0
  const cantidad = `${formatearCantidad(repuesto.stock_actual)} ${repuesto.unidad}`

  if (!repuesto.stock_bajo) {
    return <span className="whitespace-nowrap text-sm font-medium">{cantidad}</span>
  }
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${
        agotado ? 'bg-peligro-suave text-peligro' : 'bg-aviso-suave text-aviso'
      }`}
    >
      <Icono nombre="alerta" className="size-3.5" />
      {agotado ? 'Agotado' : `Stock bajo: ${cantidad}`}
    </span>
  )
}
