import { useEffect, useRef } from 'react'

import Boton from './Boton.jsx'

/**
 * Confirmación antes de acciones delicadas (prevención de errores).
 * Usa <dialog> nativo: atrapa el foco y se cierra con Escape sin código extra.
 */
export default function DialogoConfirmacion({
  abierto,
  titulo,
  mensaje,
  textoConfirmar = 'Confirmar',
  variante = 'primario',
  cargando = false,
  alConfirmar,
  alCancelar,
}) {
  const referencia = useRef(null)

  useEffect(() => {
    const dialogo = referencia.current
    if (abierto && !dialogo.open) dialogo.showModal()
    if (!abierto && dialogo.open) dialogo.close()
  }, [abierto])

  return (
    <dialog
      ref={referencia}
      onCancel={(evento) => {
        evento.preventDefault()
        alCancelar()
      }}
      className="m-auto w-[min(28rem,calc(100vw-2rem))] rounded-xl bg-superficie p-0 shadow-elevada backdrop:bg-black/40 open:animate-aparecer"
    >
      <div className="flex flex-col gap-3 p-5">
        <h2 className="text-lg font-semibold">{titulo}</h2>
        <p className="text-sm text-texto-suave">{mensaje}</p>
        <div className="mt-2 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Boton variante="secundario" onClick={alCancelar} disabled={cargando}>
            Cancelar
          </Boton>
          <Boton variante={variante} onClick={alConfirmar} cargando={cargando}>
            {textoConfirmar}
          </Boton>
        </div>
      </div>
    </dialog>
  )
}
