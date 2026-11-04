import { TIPOS_VEHICULO } from '../constantes.js'
import Icono from './Icono.jsx'

const OPCIONES = [
  { valor: null, etiqueta: 'Todos', icono: 'todos' },
  ...Object.entries(TIPOS_VEHICULO).map(([valor, { plural, icono }]) => ({
    valor,
    etiqueta: plural.charAt(0).toUpperCase() + plural.slice(1),
    icono,
  })),
]

/** Control segmentado Todos / Carros / Motos. `valor` es null (todos), 'CARRO' o 'MOTO'. */
export default function FiltroTipoVehiculo({ valor, alCambiar }) {
  return (
    <div role="group" aria-label="Tipo de vehículo" className="flex w-full rounded-lg border border-borde bg-fondo p-1 sm:inline-flex sm:w-auto sm:self-start">
      {OPCIONES.map((opcion) => {
        const activo = opcion.valor === valor
        return (
          <button
            key={opcion.etiqueta}
            type="button"
            aria-pressed={activo}
            onClick={() => alCambiar(opcion.valor)}
            className={`inline-flex min-h-10 flex-1 items-center justify-center gap-1.5 rounded-md px-3 text-sm transition-[background-color,color,box-shadow] duration-150 ease-salida sm:flex-none ${
              activo
                ? 'bg-superficie font-semibold text-primario-oscuro shadow-tarjeta'
                : 'font-medium text-texto-suave hover:text-texto'
            }`}
          >
            <Icono nombre={opcion.icono} className="size-4" />
            {opcion.etiqueta}
          </button>
        )
      })}
    </div>
  )
}
