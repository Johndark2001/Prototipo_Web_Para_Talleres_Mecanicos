// Formatos de presentación. El backend guarda los datos normalizados; aquí solo se muestran.

/** RN-20: misma regla que el backend, para que el usuario vea la placa como quedará guardada. */
export function normalizarPlaca(texto) {
  return texto.replace(/[\s-]/g, '').toUpperCase()
}

/** "3001234567" → "300 123 4567" (celular colombiano); otros números se muestran tal cual. */
export function formatearTelefono(telefono) {
  if (/^\d{10}$/.test(telefono)) {
    return `${telefono.slice(0, 3)} ${telefono.slice(3, 6)} ${telefono.slice(6)}`
  }
  return telefono
}

export function formatearFecha(iso) {
  return new Date(iso).toLocaleDateString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function describirVehiculo({ marca, modelo, anio }) {
  return [marca, modelo, anio].filter(Boolean).join(' ')
}

export function formatearFechaHora(iso) {
  return new Date(iso).toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** "2026-11-10" → "10/11/2026". Sin pasar por Date: en Colombia (UTC−5) mostraría el día anterior. */
export function formatearDia(fecha) {
  const [anio, mes, dia] = fecha.split('-')
  return `${dia}/${mes}/${anio}`
}

export function formatearKilometraje(km) {
  return `${km.toLocaleString('es-CO')} km`
}

// La API envía montos y cantidades como texto decimal ("25000.00") para no perder precisión
// (SPEC §10). Aquí solo se convierten para mostrarlos; las cuentas las hace el servidor.

/** "143500.50" → "$ 143.500,50"; sin decimales cuando son cero ("$ 25.000"). */
export function formatearPesos(valor) {
  const numero = Number(valor)
  return numero.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: Number.isInteger(numero) ? 0 : 2,
    maximumFractionDigits: 2,
  })
}

/** "4.50" → "4,5"; "2.00" → "2". */
export function formatearCantidad(valor) {
  return Number(valor).toLocaleString('es-CO', { maximumFractionDigits: 2 })
}

/**
 * Lo que el usuario escribe como precio en pesos → texto que entiende la API.
 * En Colombia "35.000" son treinta y cinco mil: se quitan puntos, espacios y "$";
 * la coma, si la hay, separa los centavos ("35.000,50" → "35000.50").
 */
export function leerPesos(texto) {
  return texto.replace(/[$\s.]/g, '').replace(',', '.')
}

/** Cantidad con coma o punto decimal ("1,5" o "1.5") → "1.5". */
export function leerCantidad(texto) {
  return texto.trim().replace(',', '.')
}
