const VARIANTES = {
  primario: 'bg-primario text-white hover:bg-primario-oscuro',
  secundario: 'bg-superficie text-texto border border-borde hover:bg-fondo',
  peligro: 'bg-peligro text-white hover:opacity-90',
  texto: 'text-primario hover:bg-primario-suave',
}

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
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${VARIANTES[variante]} ${className}`}
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
