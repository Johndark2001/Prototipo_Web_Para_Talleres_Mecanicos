import Icono from './Icono.jsx'

const ESTILOS = {
  exito: { clase: 'bg-exito-suave text-exito border-exito/30', icono: 'check' },
  error: { clase: 'bg-peligro-suave text-peligro border-peligro/30', icono: 'alerta' },
  info: { clase: 'bg-primario-suave text-primario-oscuro border-primario/30', icono: 'info' },
}

/** Mensaje visible del estado del sistema; nunca depende solo del color (RNF-07). */
export default function Aviso({ tipo = 'info', children, alCerrar }) {
  const { clase, icono } = ESTILOS[tipo]
  return (
    <div
      role={tipo === 'error' ? 'alert' : 'status'}
      className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${clase}`}
    >
      <Icono nombre={icono} className="mt-0.5 size-4 shrink-0" />
      <div className="flex-1">{children}</div>
      {alCerrar && (
        <button
          type="button"
          onClick={alCerrar}
          className="rounded p-0.5 hover:bg-black/5"
          aria-label="Cerrar mensaje"
        >
          <Icono nombre="cerrar" className="size-4" />
        </button>
      )}
    </div>
  )
}
