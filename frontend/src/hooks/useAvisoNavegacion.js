import { useState } from 'react'
import { useLocation } from 'react-router'

/**
 * Mensaje que deja la pantalla anterior al navegar, p. ej. "Cliente registrado".
 * Es de éxito salvo que la pantalla anterior envíe `avisoTipo` (p. ej. 'error').
 */
export function useAvisoNavegacion() {
  const ubicacion = useLocation()
  const [aviso, setAviso] = useState(() =>
    ubicacion.state?.aviso
      ? { tipo: ubicacion.state.avisoTipo ?? 'exito', texto: ubicacion.state.aviso }
      : null,
  )
  return [aviso, setAviso]
}
