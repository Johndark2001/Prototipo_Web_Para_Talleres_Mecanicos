import { Navigate, Outlet, useLocation } from 'react-router'

import EstadoVacio from '../components/EstadoVacio.jsx'
import PantallaCarga from '../components/PantallaCarga.jsx'
import { useSesion } from './contexto.js'

/**
 * Protege rutas en la interfaz. Es solo comodidad para el usuario: la seguridad real
 * está en el backend, que verifica sesión y rol en cada solicitud.
 */
export default function RutaProtegida({ roles, children }) {
  const { sesion, cargando } = useSesion()
  const ubicacion = useLocation()

  if (cargando) return <PantallaCarga />
  if (!sesion) return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
  if (roles && !roles.includes(sesion.usuario.rol)) {
    return (
      <EstadoVacio
        icono="candado"
        titulo="No tiene permiso para ver esta sección"
        texto="Si cree que es un error, pida al administrador del taller que revise su rol."
      />
    )
  }
  return children ?? <Outlet />
}
