import { useId, useState } from 'react'
import { Link } from 'react-router'

import { conParametros } from '../api/cliente.js'
import { formatearTelefono } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useRetrasado } from '../hooks/useRetrasado.js'
import Boton from './Boton.jsx'

/** Elige el dueño de un carro buscando entre los clientes activos del taller. */
export default function SelectorCliente({ valor, alCambiar, error, ayuda, enlaceNuevo, estadoNuevo }) {
  const id = useId()
  const [texto, setTexto] = useState('')
  const busqueda = useRetrasado(texto.trim())
  const { datos, cargando } = useConsulta(
    !valor && busqueda ? conParametros('/clientes', { q: busqueda, activo: true, page_size: 6 }) : null,
  )
  const idDescripcion = `${id}-descripcion`

  return (
    <fieldset className="flex flex-col gap-1" aria-describedby={idDescripcion}>
      <legend className="mb-1 text-sm font-medium">
        Cliente
        <span className="text-peligro" aria-hidden="true">
          {' '}
          *
        </span>
      </legend>

      {valor ? (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-borde bg-fondo px-3 py-2">
          <div className="min-w-0">
            <p className="truncate font-medium">{valor.nombre}</p>
            <p className="text-sm text-texto-suave">{formatearTelefono(valor.telefono)}</p>
          </div>
          <Boton variante="texto" onClick={() => alCambiar(null)}>
            Cambiar
          </Boton>
        </div>
      ) : (
        <>
          <label htmlFor={id} className="sr-only">
            Buscar cliente
          </label>
          <input
            id={id}
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Escriba nombre, teléfono o documento"
            autoComplete="off"
            aria-invalid={Boolean(error)}
            className={`min-h-11 w-full rounded-lg border bg-superficie px-3 text-base sm:text-sm ${
              error ? 'border-peligro' : 'border-borde'
            }`}
          />
          {busqueda && (
            <div aria-live="polite" className="text-sm">
              {cargando && !datos && <p className="py-2 text-texto-suave">Buscando…</p>}
              {datos?.data.length === 0 && (
                <p className="py-2 text-texto-suave">No hay clientes activos con «{busqueda}».</p>
              )}
              {datos?.data.length > 0 && (
                <ul className="divide-y divide-borde rounded-lg border border-borde">
                  {datos.data.map((cliente) => (
                    <li key={cliente.id}>
                      <button
                        type="button"
                        onClick={() => alCambiar(cliente)}
                        className="flex min-h-11 w-full flex-col items-start px-3 py-2 text-left transition-colors duration-150 hover:bg-fondo"
                      >
                        <span className="font-medium">{cliente.nombre}</span>
                        <span className="text-texto-suave">{formatearTelefono(cliente.telefono)}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}

      <div id={idDescripcion}>
        {ayuda && <p className="text-xs text-texto-suave">{ayuda}</p>}
        {error && <p className="text-sm text-peligro">{error}</p>}
      </div>
      {!valor && enlaceNuevo && (
        <Link to={enlaceNuevo} state={estadoNuevo} className="self-start py-2 text-sm font-semibold text-primario underline">
          ¿Cliente nuevo? Regístrelo junto con este vehículo
        </Link>
      )}
    </fieldset>
  )
}
