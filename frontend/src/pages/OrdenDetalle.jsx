import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import ChipEstado from '../components/ChipEstado.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import EtiquetaTipo from '../components/EtiquetaTipo.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import Placa from '../components/Placa.jsx'
import { claseBoton } from '../components/estilosBoton.js'
import AccionesEstado from '../components/orden/AccionesEstado.jsx'
import EnlaceSeguimiento from '../components/orden/EnlaceSeguimiento.jsx'
import HistorialOrden from '../components/orden/HistorialOrden.jsx'
import LineaTiempo from '../components/orden/LineaTiempo.jsx'
import PanelLiquidacion from '../components/orden/PanelLiquidacion.jsx'
import PanelMecanico from '../components/orden/PanelMecanico.jsx'
import PanelRecepcion from '../components/orden/PanelRecepcion.jsx'
import PanelTrabajo from '../components/orden/PanelTrabajo.jsx'
import { ESTADOS_ORDEN, ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { describirVehiculo, formatearTelefono } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useSesion } from '../sesion/contexto.js'

const textoDe = (orden) => ({
  diagnostico: orden.diagnostico ?? '',
  trabajo_realizado: orden.trabajo_realizado ?? '',
})

/** Bloque de la vista vertical de la orden (cambio #4): título y su contenido. */
function Seccion({ titulo, children }) {
  return (
    <section aria-label={titulo} className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold">{titulo}</h2>
      {children}
    </section>
  )
}

function VistaOrden({ ordenInicial }) {
  const { sesion } = useSesion()
  // El mecánico no habla con el cliente: el enlace lo comparten recepción y el administrador.
  const compartePublico = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol)
  const [orden, setOrden] = useState(ordenInicial)
  const [borrador, setBorrador] = useState(() => textoDe(ordenInicial))
  const [guardando, setGuardando] = useState(false)
  const [aviso, setAviso] = useAvisoNavegacion()
  const guardado = textoDe(orden)
  const sucio =
    borrador.diagnostico !== guardado.diagnostico ||
    borrador.trabajo_realizado !== guardado.trabajo_realizado

  function aplicar(actualizada, mensaje) {
    setOrden(actualizada)
    setBorrador(textoDe(actualizada))
    if (mensaje) setAviso({ tipo: 'exito', texto: mensaje })
  }

  async function guardarTrabajo() {
    setGuardando(true)
    try {
      aplicar(await api.patch(`/ordenes/${orden.id}`, borrador), 'Trabajo guardado')
    } catch (err) {
      setAviso({ tipo: 'error', texto: err.message })
    }
    setGuardando(false)
  }

  /** Devuelve el error para que el diálogo lo muestre si es de la nota. */
  async function cambiarEstado(transicion, nota) {
    try {
      // Lo escrito y no guardado se guarda primero: RN-17 lo revisa en el servidor.
      if (sucio) await api.patch(`/ordenes/${orden.id}`, borrador)
      const actualizada = await api.post(`/ordenes/${orden.id}/historial`, {
        estado: transicion.estado,
        nota: nota || null,
      })
      aplicar(actualizada, `Orden #${actualizada.numero}: ${ESTADOS_ORDEN[actualizada.estado].etiqueta}`)
      return null
    } catch (err) {
      if (!erroresPorCampo(err).nota) setAviso({ tipo: 'error', texto: err.message })
      return err
    }
  }

  const { vehiculo, cliente } = orden
  // Cambio #4B: el informe final solo existe para órdenes entregadas (el backend lo verifica).
  const entregada = orden.estado === 'ENTREGADO'
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Link to="/ordenes" className="inline-flex items-center gap-1 self-start text-sm text-texto-suave hover:underline">
        <Icono nombre="atras" className="size-4" />
        Órdenes
      </Link>

      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold">Orden #{orden.numero}</h1>
          <ChipEstado estado={orden.estado} />
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <Link to={`/vehiculos/${vehiculo.id}`} className="inline-flex items-center gap-2 hover:underline">
            <Placa placa={vehiculo.placa} />
            <span className="font-medium">{describirVehiculo(vehiculo)}</span>
          </Link>
          <EtiquetaTipo tipo={vehiculo.tipo} />
          <span className="inline-flex items-center gap-1 text-texto-suave">
            <Icono nombre="cliente" className="size-4" />
            <Link to={`/clientes/${cliente.id}`} className="hover:underline">
              {cliente.nombre}
            </Link>
            {cliente.telefono && (
              <>
                ·
                <a href={`tel:${cliente.telefono}`} className="underline">
                  {formatearTelefono(cliente.telefono)}
                </a>
              </>
            )}
          </span>
        </div>
      </div>

      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}

      <Seccion titulo="Estado de la orden">
        <div className="tarjeta p-4">
          <LineaTiempo estado={orden.estado} historial={orden.historial} />
        </div>
      </Seccion>

      {(orden.transiciones.length > 0 || entregada) && (
        <Seccion titulo="Acciones">
          <AccionesEstado orden={orden} alCambiarEstado={cambiarEstado} />
          {entregada && (
            <div className="flex flex-col gap-2 tarjeta p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-texto-suave">
                La orden fue entregada. Descargue el informe final para el cliente.
              </p>
              <a href={`/api/v1/ordenes/${orden.id}/informe.pdf`} download className={claseBoton('primario')}>
                <Icono nombre="descargar" className="size-4" />
                Descargar informe PDF
              </a>
            </div>
          )}
        </Seccion>
      )}

      <Seccion titulo="Información general">
        <PanelRecepcion orden={orden} alActualizar={aplicar} />
        <PanelMecanico orden={orden} alActualizar={aplicar} alError={(texto) => setAviso({ tipo: 'error', texto })} />
      </Seccion>

      {['diagnostico', 'trabajo_realizado'].map((campo) => (
        <Seccion key={campo} titulo={campo === 'diagnostico' ? 'Diagnóstico' : 'Trabajo realizado'}>
          <PanelTrabajo
            campo={campo}
            orden={orden}
            borrador={borrador}
            alCambiar={(nombre, valor) => setBorrador({ ...borrador, [nombre]: valor })}
            sucio={sucio}
            guardando={guardando}
            alGuardar={guardarTrabajo}
          />
        </Seccion>
      ))}

      <Seccion titulo="Costos">
        <PanelLiquidacion
          orden={orden}
          alActualizar={(actualizada, mensaje) => {
            // Conserva lo escrito y no guardado en diagnóstico y trabajo realizado.
            setOrden(actualizada)
            setAviso({ tipo: 'exito', texto: mensaje })
          }}
          alError={(texto) => setAviso({ tipo: 'error', texto })}
        />
      </Seccion>

      {compartePublico && (
        <Seccion titulo="Enlace de seguimiento">
          <EnlaceSeguimiento codigo={orden.codigo_seguimiento} />
        </Seccion>
      )}

      <Seccion titulo="Historial">
        <HistorialOrden historial={orden.historial} asignaciones={orden.asignaciones} />
      </Seccion>
    </div>
  )
}

export default function OrdenDetalle() {
  const { id } = useParams()
  const { datos, error, cargando, recargar } = useConsulta(`/ordenes/${id}`)

  if (error) return <ErrorCarga error={error} recurso="orden" alReintentar={recargar} />
  if (!datos || cargando) return <Esqueleto etiqueta="Cargando orden" />
  return <VistaOrden key={datos.id} ordenInicial={datos} />
}
