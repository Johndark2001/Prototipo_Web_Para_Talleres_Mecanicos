import { useState } from 'react'

import { api } from '../api/cliente.js'
import Boton from './Boton.jsx'
import DialogoConfirmacion from './DialogoConfirmacion.jsx'

/**
 * Botón de desactivar/activar con confirmación. Nada se borra (RN-11): desactivar solo
 * oculta el registro de las búsquedas habituales y conserva su historial.
 */
export default function CambioActivo({ ruta, activo, nombre, mensajeDesactivar, alCambiar }) {
  const [abierto, setAbierto] = useState(false)
  const [guardando, setGuardando] = useState(false)
  const sujeto = nombre.charAt(0).toUpperCase() + nombre.slice(1)

  async function confirmar() {
    setGuardando(true)
    try {
      const actualizado = await api.patch(ruta, { activo: !activo })
      alCambiar(actualizado, { tipo: 'exito', texto: `${sujeto} quedó ${activo ? 'inactivo' : 'activo'}` })
    } catch (err) {
      alCambiar(null, { tipo: 'error', texto: err.message })
    }
    setGuardando(false)
    setAbierto(false)
  }

  return (
    <>
      <Boton variante={activo ? 'secundario' : 'primario'} onClick={() => setAbierto(true)}>
        {activo ? 'Desactivar' : 'Activar'}
      </Boton>
      <DialogoConfirmacion
        abierto={abierto}
        titulo={activo ? `¿Desactivar ${nombre}?` : `¿Activar ${nombre}?`}
        mensaje={activo ? mensajeDesactivar : `${sujeto} volverá a aparecer en las búsquedas.`}
        textoConfirmar={activo ? 'Desactivar' : 'Activar'}
        variante={activo ? 'peligro' : 'primario'}
        cargando={guardando}
        alConfirmar={confirmar}
        alCancelar={() => setAbierto(false)}
      />
    </>
  )
}
