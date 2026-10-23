import { useCallback, useEffect, useMemo, useState } from 'react'

import { api, registrarAlExpirarSesion } from '../api/cliente.js'
import { ContextoSesion } from './contexto.js'

/**
 * La sesión vive en una cookie httpOnly que JavaScript no puede leer (ADR-005).
 * Aquí solo se guarda el usuario que devuelve /auth/me para pintar la interfaz.
 */
export default function ProveedorSesion({ children }) {
  const [sesion, setSesion] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    api
      .get('/auth/me')
      .then(setSesion)
      .catch(() => setSesion(null))
      .finally(() => setCargando(false))
  }, [])

  useEffect(() => registrarAlExpirarSesion(() => setSesion(null)), [])

  const iniciarSesion = useCallback(async (email, password) => {
    const datos = await api.post('/auth/login', { email, password })
    setSesion(datos)
    return datos
  }, [])

  const cerrarSesion = useCallback(async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      setSesion(null)
    }
  }, [])

  const valor = useMemo(
    () => ({ sesion, cargando, iniciarSesion, cerrarSesion }),
    [sesion, cargando, iniciarSesion, cerrarSesion],
  )

  return <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
}
