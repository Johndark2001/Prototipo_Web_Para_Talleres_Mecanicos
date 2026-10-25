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
