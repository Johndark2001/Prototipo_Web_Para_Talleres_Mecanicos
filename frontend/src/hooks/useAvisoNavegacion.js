import { useState } from 'react'
import { useLocation } from 'react-router'

/** Mensaje de confirmación que deja la pantalla anterior al navegar, p. ej. "Cliente registrado". */
export function useAvisoNavegacion() {
  const ubicacion = useLocation()
  const [aviso, setAviso] = useState(() =>
    ubicacion.state?.aviso ? { tipo: 'exito', texto: ubicacion.state.aviso } : null,
  )
  return [aviso, setAviso]
}
