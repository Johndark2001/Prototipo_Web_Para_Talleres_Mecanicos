import { useState } from 'react'

import { conParametros } from '../api/cliente.js'
import { useConsulta } from '../hooks/useConsulta.js'
import Aviso from './Aviso.jsx'
import EstadoVacio from './EstadoVacio.jsx'
import Esqueleto from './Esqueleto.jsx'
import Paginacion from './Paginacion.jsx'
import TarjetaOrden from './TarjetaOrden.jsx'

/**
 * Listado paginado de órdenes con los filtros de la API. El backend ya limita al mecánico
 * a sus órdenes, así que la misma lista sirve para "Mis órdenes".
 */
export default function ListaOrdenes({ filtros, vacio, mostrarVehiculo = true, tamano = 20 }) {
  const [pagina, setPagina] = useState(1)
  const clave = JSON.stringify(filtros)
  const [clavePrevia, setClavePrevia] = useState(clave)
  if (clave !== clavePrevia) {
    // Un filtro nuevo vuelve a la primera página.
    setClavePrevia(clave)
    setPagina(1)
  }
  const { datos, error, recargar } = useConsulta(
    conParametros('/ordenes', { ...filtros, page: pagina, page_size: tamano }),
  )

  if (error) {
    return (
      <Aviso tipo="error">
        {error.message}{' '}
        <button type="button" onClick={recargar} className="font-semibold underline">
          Reintentar
        </button>
      </Aviso>
    )
  }
  if (!datos) return <Esqueleto etiqueta="Cargando órdenes" />
  if (datos.data.length === 0) return <EstadoVacio icono="orden" {...vacio} />

  return (
    <div className="flex flex-col gap-3">
      <ul className="divide-y divide-borde rounded-lg border border-borde bg-superficie">
        {datos.data.map((orden) => (
          <TarjetaOrden key={orden.id} orden={orden} mostrarVehiculo={mostrarVehiculo} />
        ))}
      </ul>
      <Paginacion paginacion={datos.pagination} alCambiar={setPagina} />
    </div>
  )
}
