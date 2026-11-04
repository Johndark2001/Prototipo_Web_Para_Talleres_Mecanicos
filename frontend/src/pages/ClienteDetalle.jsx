import { Link, useParams } from 'react-router'

import AnonimizarCliente from '../components/AnonimizarCliente.jsx'
import Aviso from '../components/Aviso.jsx'
import CambioActivo from '../components/CambioActivo.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import EtiquetaTipo from '../components/EtiquetaTipo.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import Placa from '../components/Placa.jsx'
import { ROLES, ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { describirVehiculo, formatearFecha, formatearFechaHora, formatearTelefono } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useSesion } from '../sesion/contexto.js'

function Dato({ etiqueta, children }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-texto-suave">{etiqueta}</dt>
      <dd className="mt-0.5 break-words">{children || '—'}</dd>
    </div>
  )
}

function ListaVehiculos({ vehiculos }) {
  return (
    <ul className="divide-y divide-borde tarjeta">
      {vehiculos.map((vehiculo) => (
        <li key={vehiculo.id}>
          <Link
            to={`/vehiculos/${vehiculo.id}`}
            className="flex min-h-14 items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-fondo"
          >
            <Placa placa={vehiculo.placa} />
            <span className="min-w-0 flex-1 truncate">
              {describirVehiculo(vehiculo)}
              {vehiculo.color && <span className="text-texto-suave"> · {vehiculo.color}</span>}
            </span>
            <EtiquetaTipo tipo={vehiculo.tipo} />
            {!vehiculo.activo && <EtiquetaActivo activo={false} />}
            <Icono nombre="derecha" className="size-5 shrink-0 text-texto-suave" />
          </Link>
        </li>
      ))}
    </ul>
  )
}

export default function ClienteDetalle() {
  const { id } = useParams()
  const { sesion } = useSesion()
  const { datos: cliente, error, cargando, recargar } = useConsulta(`/clientes/${id}`)
  const [aviso, setAviso] = useAvisoNavegacion()

  if (error) return <ErrorCarga error={error} recurso="cliente" alReintentar={recargar} />
  if (!cliente || cargando) return <Esqueleto etiqueta="Cargando cliente" />

  // Un cliente anonimizado ya no se edita ni se reactiva (RN-11).
  const puedeEditar = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol) && !cliente.anonimizado
  const puedeAnonimizar = sesion.usuario.rol === ROLES.ADMIN && !cliente.anonimizado

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <Link to="/clientes" className="inline-flex items-center gap-1 self-start text-sm text-texto-suave hover:underline">
        <Icono nombre="atras" className="size-4" />
        Clientes
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="break-words text-2xl font-semibold">{cliente.nombre}</h1>
          <div className="mt-1">
            <EtiquetaActivo activo={cliente.activo} />
          </div>
        </div>
        {(puedeEditar || puedeAnonimizar) && (
          <div className="flex flex-wrap gap-2">
            {puedeEditar && (
              <EnlaceBoton to={`/clientes/${cliente.id}/editar`} variante="secundario">
                <Icono nombre="lapiz" className="size-4" />
                Editar
              </EnlaceBoton>
            )}
            {puedeEditar && (
              <CambioActivo
                ruta={`/clientes/${cliente.id}`}
                activo={cliente.activo}
                nombre={cliente.nombre}
                mensajeDesactivar="Dejará de aparecer en las búsquedas y no se le podrán asociar carros nuevos. Sus datos y carros se conservan."
                alCambiar={(actualizado, mensaje) => {
                  setAviso(mensaje)
                  if (actualizado) recargar()
                }}
              />
            )}
            {puedeAnonimizar && (
              <AnonimizarCliente
                cliente={cliente}
                alAnonimizar={(_, mensaje) => {
                  setAviso(mensaje)
                  recargar()
                }}
              />
            )}
          </div>
        )}
      </div>

      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}

      {cliente.anonimizado && (
        <Aviso tipo="info">
          Datos personales anonimizados el {formatearFechaHora(cliente.anonimizado_en)}
          {cliente.anonimizador && ` por ${cliente.anonimizador.nombre}`}. Sus carros y órdenes se
          conservan.
        </Aviso>
      )}

      <dl className="grid gap-4 tarjeta p-4 sm:grid-cols-2">
        <Dato etiqueta="Teléfono">
          {cliente.telefono && (
            <a href={`tel:${cliente.telefono}`} className="text-primario underline">
              {formatearTelefono(cliente.telefono)}
            </a>
          )}
        </Dato>
        <Dato etiqueta="Correo">{cliente.email}</Dato>
        <Dato etiqueta="Documento">{cliente.documento}</Dato>
        <Dato etiqueta="Autorización de datos">
          Autorizó el {formatearFecha(cliente.fecha_autorizacion)}
        </Dato>
      </dl>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Vehículos</h2>
        {puedeEditar && cliente.activo && (
          <EnlaceBoton to={`/vehiculos/nuevo?cliente=${cliente.id}`}>
            <Icono nombre="mas" />
            Vehículo
          </EnlaceBoton>
        )}
      </div>

      {cliente.vehiculos.length === 0 ? (
        <EstadoVacio
          icono="carro"
          titulo="Este cliente no tiene vehículos registrados"
          texto={puedeEditar && cliente.activo ? 'Registre su carro o su moto con el botón «+ Vehículo».' : undefined}
        />
      ) : (
        <ListaVehiculos vehiculos={cliente.vehiculos} />
      )}
    </div>
  )
}
