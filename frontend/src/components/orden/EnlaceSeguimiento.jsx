import { useState } from 'react'

import Boton from '../Boton.jsx'
import Icono from '../Icono.jsx'

/**
 * Enlace que se le comparte al cliente para que siga su carro sin cuenta (RF-13, P-4).
 * Quien lo tenga ve el estado y la liquidación, nunca datos personales (ADR-005).
 */
export default function EnlaceSeguimiento({ codigo }) {
  const [copiado, setCopiado] = useState(false)
  const url = `${window.location.origin}/seguimiento/${codigo}`

  async function copiar() {
    try {
      await navigator.clipboard.writeText(url)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2500)
    } catch {
      // Sin permiso de portapapeles: el enlace queda seleccionable en pantalla.
      setCopiado(false)
    }
  }

  return (
    <section aria-labelledby="titulo-enlace" className="flex flex-col gap-2 rounded-lg border border-borde bg-superficie p-4">
      <h2 id="titulo-enlace" className="text-xs font-medium uppercase tracking-wide text-texto-suave">
        Enlace para el cliente
      </h2>
      <p className="text-sm text-texto-suave">
        Compártalo con el cliente: verá el estado del carro y lo que se cobra, sin datos personales.
      </p>
      <p className="break-all rounded-md bg-fondo px-3 py-2 font-mono text-xs">{url}</p>
      <div className="flex flex-col gap-2 sm:flex-row">
        <Boton variante="secundario" onClick={copiar}>
          <Icono nombre={copiado ? 'check' : 'copiar'} className="size-4" />
          {copiado ? 'Copiado' : 'Copiar enlace'}
        </Boton>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold text-primario hover:bg-primario-suave"
        >
          <Icono nombre="enlace" className="size-4" />
          Ver como el cliente
        </a>
      </div>
      <span aria-live="polite" className="sr-only">
        {copiado ? 'Enlace copiado' : ''}
      </span>
    </section>
  )
}
