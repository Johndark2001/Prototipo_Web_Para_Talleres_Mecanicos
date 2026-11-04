import { useId } from 'react'

import Boton from '../Boton.jsx'

const CAMPOS = {
  diagnostico: {
    etiqueta: 'Diagnóstico',
    placeholder: 'Qué encontró al revisar el vehículo',
  },
  trabajo_realizado: {
    etiqueta: 'Trabajo realizado',
    placeholder: 'Qué se le hizo al vehículo',
    ayuda: 'Es obligatorio para marcar la orden como reparada.',
  },
}

/**
 * Diagnóstico o trabajo realizado: lo que escribe el mecánico (RF-06, RN-17). Cada uno va en
 * su propia sección; «Guardar» en cualquiera de las dos guarda ambos textos.
 */
export default function PanelTrabajo({ campo, orden, borrador, alCambiar, sucio, guardando, alGuardar }) {
  const id = useId()
  const { etiqueta, placeholder, ayuda } = CAMPOS[campo]
  const editable = orden.puede_editar_trabajo
  const valor = borrador[campo]
  const cambiado = valor !== (orden[campo] ?? '')

  return (
    <section aria-label={etiqueta} className="flex flex-col gap-2 tarjeta p-4">
      {editable ? (
        <>
          <label htmlFor={id} className="sr-only">
            {etiqueta}
          </label>
          <textarea
            id={id}
            value={valor}
            onChange={(e) => alCambiar(campo, e.target.value)}
            rows={4}
            maxLength={5000}
            placeholder={placeholder}
            aria-describedby={ayuda ? `${id}-ayuda` : undefined}
            className="w-full rounded-lg border border-borde bg-superficie px-3 py-2 text-base sm:text-sm"
          />
          {ayuda && (
            <p id={`${id}-ayuda`} className="text-xs text-texto-suave">
              {ayuda}
            </p>
          )}
          <div className="flex items-center justify-end gap-3">
            {cambiado && <span className="text-xs text-texto-suave">Cambios sin guardar</span>}
            <Boton variante="secundario" onClick={alGuardar} cargando={guardando} disabled={!sucio}>
              Guardar
            </Boton>
          </div>
        </>
      ) : (
        <p className="whitespace-pre-line break-words text-sm">{valor || <span className="text-texto-suave">Sin registrar.</span>}</p>
      )}
    </section>
  )
}
