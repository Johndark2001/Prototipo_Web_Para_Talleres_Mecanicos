import { claseBoton } from './estilosBoton.js'

/** Botón único del sistema (SPEC §11: BotonPrimario y variantes). */
export default function Boton({
  variante = 'primario',
  cargando = false,
  disabled,
  className = '',
  children,
  type = 'button',
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || cargando}
      aria-busy={cargando || undefined}
      className={claseBoton(variante, className)}
      {...props}
    >
      {cargando && (
        <span
          className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden="true"
        />
      )}
      {children}
    </button>
  )
}
