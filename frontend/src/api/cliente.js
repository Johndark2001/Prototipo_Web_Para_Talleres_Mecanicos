// Único punto de acceso a la API (ADR-004: fetch sin librerías adicionales).

export class ErrorApi extends Error {
  constructor(status, code, message, details = null) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

let alExpirarSesion = () => {}

/** Permite al proveedor de sesión reaccionar cuando una solicitud devuelve 401. */
export function registrarAlExpirarSesion(funcion) {
  alExpirarSesion = funcion
  return () => {
    alExpirarSesion = () => {}
  }
}

const RUTAS_SIN_REDIRECCION = ['/auth/login', '/auth/me']

async function solicitar(metodo, ruta, cuerpo) {
  const opciones = {
    method: metodo,
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }
  if (metodo !== 'GET') {
    // La API rechaza modificaciones que no sean JSON (defensa CSRF, ADR-005).
    opciones.headers['Content-Type'] = 'application/json'
    opciones.body = JSON.stringify(cuerpo ?? {})
  }

  let respuesta
  try {
    respuesta = await fetch(`/api/v1${ruta}`, opciones)
  } catch {
    throw new ErrorApi(
      0,
      'SIN_CONEXION',
      'No hay conexión con el servidor. Revise su internet e intente de nuevo.',
    )
  }

  if (respuesta.status === 204) return null
  const datos = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    if (respuesta.status === 401 && !RUTAS_SIN_REDIRECCION.includes(ruta)) {
      alExpirarSesion()
    }
    const error = datos?.error
    throw new ErrorApi(
      respuesta.status,
      error?.code ?? 'ERROR',
      error?.message ?? 'Ocurrió un error inesperado. Intente de nuevo.',
      error?.details ?? null,
    )
  }
  return datos
}

export const api = {
  get: (ruta) => solicitar('GET', ruta),
  post: (ruta, cuerpo) => solicitar('POST', ruta, cuerpo),
  patch: (ruta, cuerpo) => solicitar('PATCH', ruta, cuerpo),
  // También lleva cuerpo JSON: la API exige JSON en toda modificación (defensa CSRF).
  borrar: (ruta) => solicitar('DELETE', ruta),
}

/** Arma "/ruta?a=1&b=2" omitiendo los parámetros vacíos; URLSearchParams escapa los valores. */
export function conParametros(ruta, parametros) {
  const consulta = new URLSearchParams(
    Object.entries(parametros).filter(([, valor]) => valor !== undefined && valor !== null && valor !== ''),
  ).toString()
  return consulta ? `${ruta}?${consulta}` : ruta
}

/** Convierte los detalles de un 422 en { campo: mensaje } para los formularios. */
export function erroresPorCampo(error) {
  if (!(error instanceof ErrorApi) || !Array.isArray(error.details)) return {}
  return Object.fromEntries(error.details.map((d) => [d.campo, d.mensaje]))
}
