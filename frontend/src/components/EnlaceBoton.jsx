import { Link } from 'react-router'

import { claseBoton } from './estilosBoton.js'

/** Enlace con apariencia de botón: navega a otra pantalla (nuevo, editar, cancelar). */
export default function EnlaceBoton({ to, variante = 'primario', className = '', children, ...props }) {
  return (
    <Link to={to} className={claseBoton(variante, className)} {...props}>
      {children}
    </Link>
  )
}
