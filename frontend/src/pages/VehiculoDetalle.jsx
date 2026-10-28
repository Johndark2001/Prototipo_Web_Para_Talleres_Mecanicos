import { Link, useParams } from 'react-router'

import { conParametros } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import CambioActivo from '../components/CambioActivo.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import ListaOrdenes from '../components/ListaOrdenes.jsx'
import Placa from '../components/Placa.jsx'
import { ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { describirVehiculo, formatearTelefono } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useSesion } from '../sesion/contexto.js'

/** RN-08: si el carro ya tiene una orden abierta, se lleva a ella en vez de abrir otra. */
function AccesoOrden({ vehiculoId }) {
  const { datos } = useConsulta(
    conParametros('/ordenes', { vehiculo_id: vehiculoId, abiertas: true, page_size: 1 }),
  )
  if (!datos) return null
  const abierta = datos.data[0]
  if (abierta) {
    return (
      <EnlaceBoton to={`/ordenes/${abierta.id}`} variante="secundario">
        Ver orden abierta #{abierta.numero}
      </EnlaceBoton>
    )
  }
  return (
    <EnlaceBoton to={`/ordenes/nueva?vehiculo=${vehiculoId}`}>
      <Icono nombre="mas" />
      Nueva orden para este carro
    </EnlaceBoton>
  )
}

export default function VehiculoDetalle() {
  const { id } = useParams()
  const { sesion } = useSesion()
  const puedeEditar = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol)
  const { datos: vehiculo, error, cargando, recargar } = useConsulta(`/vehiculos/${id}`)
  const [aviso, setAviso] = useAvisoNavegacion()

  if (error) return <ErrorCarga error={error} recurso="vehiculo" alReintentar={recargar} />
  if (!vehiculo || cargando) return <Esqueleto etiqueta="Cargando carro" />
  const { cliente } = vehiculo

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <Link
        to="/vehiculos"
        className="inline-flex items-center gap-1 self-start text-sm text-texto-suave hover:underline"
      >
        <Icono nombre="atras" className="size-4" />
        Vehículos
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-2">
          <h1 className="sr-only">Carro de placa {vehiculo.placa}</h1>
          <Placa placa={vehiculo.placa} grande />
          <p className="text-lg font-medium">
            {describirVehiculo(vehiculo)}
            {vehiculo.color && <span className="text-texto-suave"> · {vehiculo.color}</span>}
          </p>
          <div>
            <EtiquetaActivo activo={vehiculo.activo} />
          </div>
        </div>
        {puedeEditar && (
          <div className="flex gap-2">
            <EnlaceBoton to={`/vehiculos/${vehiculo.id}/editar`} variante="secundario">
              <Icono nombre="lapiz" className="size-4" />
              Editar
            </EnlaceBoton>
            <CambioActivo
              ruta={`/vehiculos/${vehiculo.id}`}
              activo={vehiculo.activo}
              nombre={`el carro ${vehiculo.placa}`}
              mensajeDesactivar="Dejará de aparecer en las búsquedas. Su historial se conserva y puede activarlo de nuevo."
              alCambiar={(actualizado, mensaje) => {
                setAviso(mensaje)
                if (actualizado) recargar()
              }}
            />
          </div>
        )}
      </div>

      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}

      <section
        aria-labelledby="titulo-dueno"
        className="flex flex-col gap-1 rounded-lg border border-borde bg-superficie p-4"
      >
        <h2 id="titulo-dueno" className="text-xs font-medium uppercase tracking-wide text-texto-suave">
          Dueño
        </h2>
        <Link to={`/clientes/${cliente.id}`} className="flex items-center gap-2 font-medium text-primario hover:underline">
          <Icono nombre="cliente" className="size-4" />
          {cliente.nombre}
          {!cliente.activo && <span className="text-sm font-normal text-texto-suave">(inactivo)</span>}
        </Link>
        {cliente.telefono && (
          <a href={`tel:${cliente.telefono}`} className="self-start text-sm text-texto-suave underline">
            {formatearTelefono(cliente.telefono)}
          </a>
        )}
      </section>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Historial de mantenimiento</h2>
        {puedeEditar && vehiculo.activo && cliente.activo && (
          <AccesoOrden vehiculoId={vehiculo.id} />
        )}
      </div>
      <ListaOrdenes
        filtros={{ vehiculo_id: vehiculo.id }}
        mostrarVehiculo={false}
        vacio={{
          titulo: 'Este carro todavía no tiene órdenes',
          texto: 'Aquí aparecerán sus órdenes de trabajo: fecha, motivo, mecánico y estado.',
        }}
      />
    </div>
  )
}
