import Icono from './Icono.jsx'

/** Pantalla vacía que explica qué hacer (heurística de ayuda y aprendizaje). */
export default function EstadoVacio({ icono = 'info', titulo, texto, children }) {
  return (
    <div
      role="status"
      className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-borde bg-superficie px-6 py-12 text-center"
    >
      <Icono nombre={icono} className="size-10 text-texto-suave" />
      <h2 className="text-base font-semibold">{titulo}</h2>
      {texto && <p className="max-w-md text-sm text-texto-suave">{texto}</p>}
      {children && <div className="mt-2">{children}</div>}
    </div>
  )
}
