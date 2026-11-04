import { TIPOS_VEHICULO } from '../constantes.js'
import Icono from './Icono.jsx'

/** Tipo del vehículo con ícono y texto: «Carro» o «Moto». */
export default function EtiquetaTipo({ tipo }) {
  const { etiqueta, icono } = TIPOS_VEHICULO[tipo] ?? TIPOS_VEHICULO.CARRO
  return (
    <span className="inline-flex shrink-0 items-center gap-1 rounded-full border border-borde bg-fondo px-2 py-0.5 text-xs font-medium text-texto-suave">
      <Icono nombre={icono} className="size-3.5" />
      {etiqueta}
    </span>
  )
}
