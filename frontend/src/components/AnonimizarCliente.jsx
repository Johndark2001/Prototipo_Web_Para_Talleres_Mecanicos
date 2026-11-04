import { useEffect, useId, useRef, useState } from 'react'

import { api } from '../api/cliente.js'
import Boton from './Boton.jsx'

const PALABRA = 'ANONIMIZAR'

/**
 * Anonimización del cliente (RN-11, RNF-06), solo para el ADMIN. No se puede deshacer, por eso
 * pide escribir la palabra además de pulsar el botón (prevención de errores).
 */
export default function AnonimizarCliente({ cliente, alAnonimizar }) {
  const referencia = useRef(null)
  const id = useId()
  const [abierto, setAbierto] = useState(false)
  const [texto, setTexto] = useState('')
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const confirmado = texto.trim().toUpperCase() === PALABRA

  useEffect(() => {
    const dialogo = referencia.current
    if (abierto && !dialogo.open) {
      setTexto('')
      setError(null)
      dialogo.showModal()
    }
    if (!abierto && dialogo.open) dialogo.close()
  }, [abierto])

  async function confirmar(evento) {
    evento.preventDefault()
    if (!confirmado) {
      setError(`Escriba ${PALABRA} para confirmar`)
      return
    }
    setGuardando(true)
    try {
      const actualizado = await api.post(`/clientes/${cliente.id}/anonimizar`, { confirmacion: PALABRA })
      setAbierto(false)
      alAnonimizar(actualizado, { tipo: 'exito', texto: 'Los datos personales del cliente se anonimizaron' })
    } catch (err) {
      setError(err.message)
    }
    setGuardando(false)
  }

  return (
    <>
      <Boton variante="secundario" onClick={() => setAbierto(true)}>
        Anonimizar
      </Boton>
      <dialog
        ref={referencia}
        onCancel={(evento) => {
          evento.preventDefault()
          if (!guardando) setAbierto(false)
        }}
        className="m-auto w-[min(32rem,calc(100vw-2rem))] rounded-xl bg-superficie p-0 shadow-elevada backdrop:bg-black/40 open:animate-aparecer"
      >
        <form onSubmit={confirmar} noValidate className="flex flex-col gap-3 p-5">
          <h2 className="text-lg font-semibold">¿Anonimizar a {cliente.nombre}?</h2>
          <div className="flex flex-col gap-2 text-sm text-texto-suave">
            <p>
              Se borran para siempre su nombre, teléfono, correo y documento. Úselo cuando el cliente
              pida eliminar sus datos (Ley 1581).
            </p>
            <p>
              Sus carros, órdenes e historial se conservan, y el enlace de seguimiento sigue
              funcionando. El cliente queda inactivo y <strong>esto no se puede deshacer</strong>.
            </p>
          </div>
          <label htmlFor={id} className="text-sm font-medium">
            Escriba <span className="font-mono">{PALABRA}</span> para confirmar
          </label>
          <input
            id={id}
            value={texto}
            onChange={(e) => {
              setTexto(e.target.value)
              setError(null)
            }}
            autoComplete="off"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? `${id}-error` : undefined}
            className={`w-full rounded-lg border bg-superficie px-3 py-2 text-base sm:text-sm ${
              error ? 'border-peligro' : 'border-borde'
            }`}
          />
          {error && (
            <p id={`${id}-error`} role="alert" className="text-sm text-peligro">
              {error}
            </p>
          )}
          <div className="mt-2 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Boton variante="secundario" onClick={() => setAbierto(false)} disabled={guardando}>
              Volver
            </Boton>
            <Boton type="submit" variante="peligro" cargando={guardando} disabled={!confirmado}>
              Anonimizar
            </Boton>
          </div>
        </form>
      </dialog>
    </>
  )
}
