import { useEffect, useId, useRef, useState } from 'react'

import Boton from './Boton.jsx'

/** Confirmación que pide escribir una nota: motivo de cancelación, retroceso, repuesto faltante. */
export default function DialogoNota({
  abierto,
  titulo,
  mensaje,
  etiqueta,
  obligatoria = false,
  textoConfirmar,
  variante = 'primario',
  cargando = false,
  error,
  alConfirmar,
  alCancelar,
}) {
  const referencia = useRef(null)
  const id = useId()
  const [nota, setNota] = useState('')
  const [falta, setFalta] = useState(false)

  useEffect(() => {
    const dialogo = referencia.current
    if (abierto && !dialogo.open) {
      setNota('')
      setFalta(false)
      dialogo.showModal()
    }
    if (!abierto && dialogo.open) dialogo.close()
  }, [abierto])

  function confirmar(evento) {
    evento.preventDefault()
    if (obligatoria && !nota.trim()) {
      setFalta(true)
      return
    }
    alConfirmar(nota.trim())
  }

  const mensajeError = falta ? 'Este campo es obligatorio' : error

  return (
    <dialog
      ref={referencia}
      onCancel={(evento) => {
        evento.preventDefault()
        alCancelar()
      }}
      className="m-auto w-[min(32rem,calc(100vw-2rem))] rounded-xl bg-superficie p-0 shadow-elevada backdrop:bg-black/40 open:animate-aparecer"
    >
      <form onSubmit={confirmar} noValidate className="flex flex-col gap-3 p-5">
        <h2 className="text-lg font-semibold">{titulo}</h2>
        {mensaje && <p className="text-sm text-texto-suave">{mensaje}</p>}
        <label htmlFor={id} className="text-sm font-medium">
          {etiqueta}
          {obligatoria ? (
            <span className="text-peligro" aria-hidden="true">
              {' '}
              *
            </span>
          ) : (
            <span className="font-normal text-texto-suave"> (opcional)</span>
          )}
        </label>
        <textarea
          id={id}
          value={nota}
          onChange={(e) => setNota(e.target.value)}
          rows={3}
          maxLength={1000}
          required={obligatoria}
          aria-invalid={Boolean(mensajeError)}
          aria-describedby={mensajeError ? `${id}-error` : undefined}
          className={`w-full rounded-lg border bg-superficie px-3 py-2 text-base sm:text-sm ${
            mensajeError ? 'border-peligro' : 'border-borde'
          }`}
        />
        {mensajeError && (
          <p id={`${id}-error`} className="text-sm text-peligro">
            {mensajeError}
          </p>
        )}
        <div className="mt-2 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Boton variante="secundario" onClick={alCancelar} disabled={cargando}>
            Volver
          </Boton>
          <Boton type="submit" variante={variante} cargando={cargando}>
            {textoConfirmar}
          </Boton>
        </div>
      </form>
    </dialog>
  )
}
