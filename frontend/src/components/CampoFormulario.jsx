import { useId } from 'react'

/** Campo con etiqueta visible, ayuda y error asociados por ARIA (RNF-07). */
export default function CampoFormulario({
  etiqueta,
  error,
  ayuda,
  obligatorio = false,
  className = '',
  children,
  ...propsInput
}) {
  const id = useId()
  const idAyuda = ayuda ? `${id}-ayuda` : undefined
  const idError = error ? `${id}-error` : undefined
  const descripcion = [idAyuda, idError].filter(Boolean).join(' ') || undefined
  const estilo = `min-h-11 w-full rounded-md border bg-superficie px-3 text-base sm:text-sm ${
    error ? 'border-peligro' : 'border-borde'
  }`

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label htmlFor={id} className="text-sm font-medium text-texto">
        {etiqueta}
        {obligatorio && (
          <span className="text-peligro" aria-hidden="true">
            {' '}
            *
          </span>
        )}
      </label>
      {children ? (
        children({ id, className: estilo, 'aria-invalid': Boolean(error), 'aria-describedby': descripcion })
      ) : (
        <input
          id={id}
          className={estilo}
          aria-invalid={Boolean(error)}
          aria-describedby={descripcion}
          required={obligatorio}
          {...propsInput}
        />
      )}
      {ayuda && (
        <p id={idAyuda} className="text-xs text-texto-suave">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={idError} className="text-sm text-peligro">
          {error}
        </p>
      )}
    </div>
  )
}
