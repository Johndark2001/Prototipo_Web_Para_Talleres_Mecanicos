/** Marcador de carga para contenido (en lugar de un spinner suelto). */
export default function Esqueleto({ filas = 3, etiqueta = 'Cargando' }) {
  return (
    <div className="flex flex-col gap-3" aria-busy="true" aria-label={etiqueta}>
      {Array.from({ length: filas }, (_, i) => (
        <div key={i} className="h-12 animate-pulse rounded-md bg-borde" />
      ))}
    </div>
  )
}
