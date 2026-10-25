import { useId } from 'react'

import Boton from '../Boton.jsx'

function AreaTexto({ etiqueta, valor, alCambiar, editable, ayuda, placeholder }) {
  const id = useId()
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium">
        {etiqueta}
      </label>
      {editable ? (
        <textarea
          id={id}
          value={valor}
          onChange={(e) => alCambiar(e.target.value)}
          rows={3}
          maxLength={5000}
          placeholder={placeholder}
          aria-describedby={ayuda ? `${id}-ayuda` : undefined}
          className="w-full rounded-md border border-borde bg-superficie px-3 py-2 text-base sm:text-sm"
        />
      ) : (
        <p id={id} className="whitespace-pre-line rounded-md bg-fondo px-3 py-2 text-sm">
          {valor || '—'}
        </p>
      )}
      {editable && ayuda && (
        <p id={`${id}-ayuda`} className="text-xs text-texto-suave">
          {ayuda}
        </p>
      )}
    </div>
  )
}

/** Diagnóstico y trabajo realizado: lo que escribe el mecánico (RF-06, RN-17). */
export default function PanelTrabajo({ orden, borrador, alCambiar, sucio, guardando, alGuardar }) {
  const editable = orden.puede_editar_trabajo

  return (
    <section
      aria-labelledby="titulo-trabajo"
      className="flex flex-col gap-3 rounded-lg border border-borde bg-superficie p-4"
    >
      <h2 id="titulo-trabajo" className="text-base font-semibold">
        Trabajo en el carro
      </h2>
      <AreaTexto
        etiqueta="Diagnóstico"
        valor={borrador.diagnostico}
        alCambiar={(v) => alCambiar('diagnostico', v)}
        editable={editable}
        placeholder="Qué encontró al revisar el carro"
      />
      <AreaTexto
        etiqueta="Trabajo realizado"
        valor={borrador.trabajo_realizado}
        alCambiar={(v) => alCambiar('trabajo_realizado', v)}
        editable={editable}
        placeholder="Qué se le hizo al carro"
        ayuda="Es obligatorio para marcar la orden como reparada."
      />
      {editable && (
        <div className="flex items-center justify-end gap-3">
          {sucio && <span className="text-xs text-texto-suave">Cambios sin guardar</span>}
          <Boton variante="secundario" onClick={alGuardar} cargando={guardando} disabled={!sucio}>
            Guardar
          </Boton>
        </div>
      )}
    </section>
  )
}
