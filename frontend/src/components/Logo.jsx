import { useId } from 'react'

// Marca de Taller Digital: un engranaje (la mecánica) con su eje, sobre la placa verde del
// taller, y un punto amarillo de placa que lo vuelve "digital". SVG propio (ADR-004).
// Los dientes salen de un trazo punteado sobre el anillo exterior: 10 dientes iguales.
const DIENTES = (2 * Math.PI * 8.6) / 10

export function MarcaLogo({ className = 'size-9' }) {
  // Id propio por instancia: el logo aparece a la vez en la barra lateral y en el encabezado.
  const brillo = useId()
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="#0f766e" />
      <rect width="32" height="32" rx="8" fill={`url(#${brillo})`} />
      <defs>
        <linearGradient id={brillo} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffffff" stopOpacity="0.16" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <g fill="none" stroke="#ffffff" transform="rotate(-9 16 16)">
        <circle cx="16" cy="16" r="8.6" strokeWidth="3" strokeDasharray={`${DIENTES / 2} ${DIENTES / 2}`} />
        <circle cx="16" cy="16" r="6.4" strokeWidth="2.2" />
      </g>
      <circle cx="16" cy="16" r="2.2" fill="#ffffff" />
      <rect x="23.5" y="4.5" width="4" height="4" rx="1.2" fill="#facc15" />
    </svg>
  )
}

/** Logo completo: marca más nombre. `tono="claro"` es para fondos oscuros. */
export default function Logo({ tono = 'oscuro', className = '', tamano = 'size-9' }) {
  const claro = tono === 'claro'
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <MarcaLogo className={`${tamano} shrink-0`} />
      <span className={`text-lg leading-none tracking-tight ${claro ? 'text-white' : 'text-texto'}`}>
        <span className="font-bold">Taller</span>{' '}
        <span className={`font-medium ${claro ? 'text-lateral-activo' : 'text-primario'}`}>Digital</span>
      </span>
    </span>
  )
}
