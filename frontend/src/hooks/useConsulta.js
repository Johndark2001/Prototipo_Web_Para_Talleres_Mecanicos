import { useCallback, useEffect, useState } from 'react'

import { api } from '../api/cliente.js'

/**
 * Carga una ruta GET de la API. Si la ruta cambia (por ejemplo, al escribir en un buscador)
 * descarta las respuestas viejas, para que una respuesta lenta no pise a la más reciente.
 * Mientras llega la nueva respuesta conserva los datos anteriores en pantalla.
 * Con `ruta` nula no consulta nada.
 */
export function useConsulta(ruta) {
  const [estado, setEstado] = useState({ ruta: null, datos: null, error: null })
  const [version, setVersion] = useState(0)

  useEffect(() => {
    if (!ruta) return undefined
    let vigente = true
    api
      .get(ruta)
      .then((datos) => vigente && setEstado({ ruta, datos, error: null }))
      .catch((error) => vigente && setEstado((previo) => ({ ...previo, ruta, error })))
    return () => {
      vigente = false
    }
  }, [ruta, version])

  const recargar = useCallback(() => setVersion((v) => v + 1), [])

  return {
    datos: ruta ? estado.datos : null,
    error: ruta ? estado.error : null,
    cargando: Boolean(ruta) && estado.ruta !== ruta,
    recargar,
  }
}
