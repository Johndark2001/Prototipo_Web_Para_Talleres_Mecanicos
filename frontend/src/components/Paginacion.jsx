import Boton from './Boton.jsx'

/** Paginación simple de anterior/siguiente (simplificación aceptada del MVP, SPEC §17.1). */
export default function Paginacion({ paginacion, alCambiar }) {
  if (!paginacion || paginacion.total_pages <= 1) return null
  const { page, total_pages: totalPaginas } = paginacion

  return (
    <nav aria-label="Paginación" className="flex items-center justify-between gap-2">
      <Boton variante="secundario" disabled={page <= 1} onClick={() => alCambiar(page - 1)}>
        Anterior
      </Boton>
      <span className="text-sm text-texto-suave">
        Página {page} de {totalPaginas}
      </span>
      <Boton
        variante="secundario"
        disabled={page >= totalPaginas}
        onClick={() => alCambiar(page + 1)}
      >
        Siguiente
      </Boton>
    </nav>
  )
}
