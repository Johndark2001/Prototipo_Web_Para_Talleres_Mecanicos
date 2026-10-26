import { useId, useState } from 'react'

import { conParametros } from '../../api/cliente.js'
import { formatearPesos } from '../../formato.js'
import { useConsulta } from '../../hooks/useConsulta.js'
import { useRetrasado } from '../../hooks/useRetrasado.js'
import Boton from '../Boton.jsx'
import EtiquetaStock from '../EtiquetaStock.jsx'

/** Busca un repuesto activo por nombre o código mostrando cuánto queda (prevención de errores). */
export default function SelectorRepuesto({ valor, alCambiar, error }) {
  const id = useId()
  const [texto, setTexto] = useState('')
  const busqueda = useRetrasado(texto.trim())
  const { datos, cargando } = useConsulta(
    !valor && busqueda
      ? conParametros('/repuestos', { buscar: busqueda, activo: true, page_size: 6 })
      : null,
  )

  if (valor) {
    return (
      <div className="flex flex-col gap-1">
        <span className="text-sm font-medium">Repuesto</span>
        <div className="flex items-center justify-between gap-3 rounded-md border border-borde bg-fondo px-3 py-2">
          <div className="min-w-0">
            <p className="truncate font-medium">{valor.nombre}</p>
            <p className="flex flex-wrap items-center gap-2 text-sm text-texto-suave">
              {formatearPesos(valor.precio_venta)} / {valor.unidad} · Hay:
              <EtiquetaStock repuesto={valor} />
            </p>
          </div>
          <Boton variante="texto" onClick={() => alCambiar(null)}>
            Cambiar
          </Boton>
        </div>
        {error && <p className="text-sm text-peligro">{error}</p>}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium">
        Repuesto
        <span className="text-peligro" aria-hidden="true">
          {' '}
          *
        </span>
      </label>
      <input
        id={id}
        type="search"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Escriba el nombre o el código"
        autoComplete="off"
        aria-invalid={Boolean(error)}
        className={`min-h-11 w-full rounded-md border bg-superficie px-3 text-base sm:text-sm ${
          error ? 'border-peligro' : 'border-borde'
        }`}
      />
      {busqueda && (
        <div aria-live="polite" className="text-sm">
          {cargando && !datos && <p className="py-2 text-texto-suave">Buscando…</p>}
          {datos?.data.length === 0 && (
            <p className="py-2 text-texto-suave">No hay repuestos activos con «{busqueda}».</p>
          )}
          {datos?.data.length > 0 && (
            <ul className="divide-y divide-borde rounded-md border border-borde">
              {datos.data.map((repuesto) => {
                const agotado = Number(repuesto.stock_actual) === 0
                return (
                  <li key={repuesto.id}>
                    <button
                      type="button"
                      onClick={() => alCambiar(repuesto)}
                      disabled={agotado}
                      className="flex min-h-11 w-full items-center justify-between gap-3 px-3 py-2 text-left hover:bg-fondo disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <span className="min-w-0">
                        <span className="block truncate font-medium">{repuesto.nombre}</span>
                        <span className="block text-texto-suave">
                          <span className="font-mono">{repuesto.codigo}</span> · {formatearPesos(repuesto.precio_venta)}
                        </span>
                      </span>
                      <EtiquetaStock repuesto={repuesto} />
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      )}
      {error && <p className="text-sm text-peligro">{error}</p>}
    </div>
  )
}
