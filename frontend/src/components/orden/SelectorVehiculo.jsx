import { useState } from 'react'
import { Link } from 'react-router'

import { conParametros } from '../../api/cliente.js'
import { describirVehiculo, normalizarPlaca } from '../../formato.js'
import { useConsulta } from '../../hooks/useConsulta.js'
import { useRetrasado } from '../../hooks/useRetrasado.js'
import Boton from '../Boton.jsx'
import EtiquetaTipo from '../EtiquetaTipo.jsx'
import Placa from '../Placa.jsx'

/** Paso 1 de la recepción: buscar la placa (SPEC §11, flujo de recepción). */
export default function SelectorVehiculo({ valor, alCambiar, error }) {
  const [texto, setTexto] = useState('')
  const placa = useRetrasado(normalizarPlaca(texto))
  const { datos, cargando } = useConsulta(
    !valor && placa ? conParametros('/vehiculos', { placa, activo: true, page_size: 6 }) : null,
  )

  if (valor) {
    return (
      <div className="flex items-center justify-between gap-3 rounded-lg border border-borde bg-fondo px-3 py-2">
        <div className="flex min-w-0 items-center gap-3">
          <Placa placa={valor.placa} />
          <div className="min-w-0">
            <p className="flex min-w-0 items-center gap-2">
              <span className="truncate font-medium">{describirVehiculo(valor)}</span>
              <EtiquetaTipo tipo={valor.tipo} />
            </p>
            <p className="truncate text-sm text-texto-suave">Cliente: {valor.cliente.nombre}</p>
          </div>
        </div>
        <Boton variante="texto" onClick={() => alCambiar(null)}>
          Cambiar
        </Boton>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="placa-recepcion" className="text-sm font-medium">
        Placa del carro
        <span className="text-peligro" aria-hidden="true">
          {' '}
          *
        </span>
      </label>
      <input
        id="placa-recepcion"
        type="search"
        value={texto}
        onChange={(e) => setTexto(e.target.value.toUpperCase())}
        placeholder="ABC123"
        autoComplete="off"
        autoCapitalize="characters"
        autoFocus
        maxLength={12}
        aria-invalid={Boolean(error)}
        className={`min-h-11 w-full rounded-lg border bg-superficie px-3 font-mono text-base uppercase sm:text-sm ${
          error ? 'border-peligro' : 'border-borde'
        }`}
      />
      {error && <p className="text-sm text-peligro">{error}</p>}
      {placa && (
        <div aria-live="polite" className="text-sm">
          {cargando && !datos && <p className="py-2 text-texto-suave">Buscando…</p>}
          {datos?.data.length === 0 && (
            <p className="py-2">
              No hay carros activos con «{placa}».{' '}
              <Link to="/vehiculos/nuevo" state={{ placa }} className="font-semibold text-primario underline">
                Registrar el carro
              </Link>
            </p>
          )}
          {datos?.data.length > 0 && (
            <ul className="mt-1 divide-y divide-borde rounded-lg border border-borde">
              {datos.data.map((vehiculo) => (
                <li key={vehiculo.id}>
                  <button
                    type="button"
                    onClick={() => alCambiar(vehiculo)}
                    className="flex min-h-11 w-full items-center gap-3 px-3 py-2 text-left transition-colors duration-150 hover:bg-fondo"
                  >
                    <Placa placa={vehiculo.placa} />
                    <span className="min-w-0 flex-1 truncate">
                      {describirVehiculo(vehiculo)} · {vehiculo.cliente.nombre}
                    </span>
                    <EtiquetaTipo tipo={vehiculo.tipo} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
