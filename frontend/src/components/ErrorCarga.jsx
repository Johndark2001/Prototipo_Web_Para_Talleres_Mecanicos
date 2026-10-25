import { Link } from 'react-router'

import Aviso from './Aviso.jsx'
import EstadoVacio from './EstadoVacio.jsx'

const RECURSOS = {
  cliente: { titulo: 'Este cliente no existe', volver: '/clientes', texto: 'Ver clientes' },
  vehiculo: { titulo: 'Este carro no existe', volver: '/vehiculos', texto: 'Ver vehículos' },
}

/**
 * Error al cargar un registro. "No existe" y "es de otro taller" se ven igual (ADR-006);
 * un identificador mal escrito en la dirección (422) también se trata como inexistente.
 */
export default function ErrorCarga({ error, recurso, alReintentar }) {
  if (error.status === 404 || error.status === 422) {
    const { titulo, volver, texto } = RECURSOS[recurso]
    return (
      <EstadoVacio icono="alerta" titulo={titulo} texto="Revise la dirección o búsquelo de nuevo.">
        <Link to={volver} className="font-semibold text-primario underline">
          {texto}
        </Link>
      </EstadoVacio>
    )
  }
  return (
    <Aviso tipo="error">
      {error.message}{' '}
      <button type="button" onClick={alReintentar} className="font-semibold underline">
        Reintentar
      </button>
    </Aviso>
  )
}
