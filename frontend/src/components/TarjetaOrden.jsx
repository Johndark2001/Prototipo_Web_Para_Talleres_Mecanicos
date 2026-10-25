import { Link } from 'react-router'

import { describirVehiculo, formatearFecha } from '../formato.js'
import ChipEstado from './ChipEstado.jsx'
import Icono from './Icono.jsx'
import Placa from './Placa.jsx'

/** Una orden en un listado (SPEC §11: TarjetaOrden). */
export default function TarjetaOrden({ orden, mostrarVehiculo = true }) {
  return (
    <li>
      <Link
        to={`/ordenes/${orden.id}`}
        className="flex min-h-16 items-center gap-3 px-4 py-3 hover:bg-fondo"
      >
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">#{orden.numero}</span>
            {mostrarVehiculo && <Placa placa={orden.vehiculo.placa} />}
            <ChipEstado estado={orden.estado} />
          </div>
          <p className="truncate text-sm">
            {mostrarVehiculo && <span className="font-medium">{describirVehiculo(orden.vehiculo)} · </span>}
            {orden.motivo_ingreso}
          </p>
          <p className="truncate text-xs text-texto-suave">
            {formatearFecha(orden.fecha_ingreso)} · {orden.mecanico ? orden.mecanico.nombre : 'Sin mecánico'}
          </p>
        </div>
        <Icono nombre="derecha" className="size-5 shrink-0 text-texto-suave" />
      </Link>
    </li>
  )
}
