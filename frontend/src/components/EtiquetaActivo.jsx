import Icono from './Icono.jsx'

/** Indica si un registro está activo con ícono y texto, no solo con color (RNF-07). */
export default function EtiquetaActivo({ activo }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${
        activo ? 'bg-exito-suave text-exito' : 'bg-fondo text-texto-suave'
      }`}
    >
      <Icono nombre={activo ? 'check' : 'candado'} className="size-3.5" />
      {activo ? 'Activo' : 'Inactivo'}
    </span>
  )
}
