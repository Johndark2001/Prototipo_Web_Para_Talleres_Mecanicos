import { Link } from 'react-router'

const VARIANTES = {
  primario: 'bg-primario text-white hover:bg-primario-oscuro',
  secundario: 'bg-superficie text-texto border border-borde hover:bg-fondo',
}

/** Enlace con apariencia de botón: navega a otra pantalla (nuevo, editar, cancelar). */
export default function EnlaceBoton({ to, variante = 'primario', className = '', children, ...props }) {
  return (
    <Link
      to={to}
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold ${VARIANTES[variante]} ${className}`}
      {...props}
    >
      {children}
    </Link>
  )
}
