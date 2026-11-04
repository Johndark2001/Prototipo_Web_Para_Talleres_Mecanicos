// Categoría del problema con que entra el vehículo (cambio #5). El catálogo lo sirve la API
// (/catalogos/categorias-problema) según el tipo de vehículo.

export const OTRO = 'Otro'

/** Sin tildes ni mayúsculas: «bateria» encuentra «Problemas de batería». */
export function claveBusqueda(texto) {
  return texto.normalize('NFD').replace(/\p{Mn}/gu, '').toLowerCase().trim()
}

/** Texto que se muestra: con «Otro», el detalle escrito. */
export function nombreProblema(orden) {
  if (orden.categoria_problema === OTRO && orden.categoria_otro) return `${OTRO}: ${orden.categoria_otro}`
  return orden.categoria_problema
}
