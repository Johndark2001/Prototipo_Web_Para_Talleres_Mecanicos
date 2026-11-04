import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import CamposProblema from '../components/orden/CamposProblema.jsx'
import SelectorMecanico from '../components/orden/SelectorMecanico.jsx'
import SelectorVehiculo from '../components/orden/SelectorVehiculo.jsx'
import { useConsulta } from '../hooks/useConsulta.js'
import { OTRO } from '../problema.js'

function Formulario({ vehiculoInicial }) {
  const navegar = useNavigate()
  const [vehiculo, setVehiculo] = useState(vehiculoInicial)
  const [tipoElegido, setTipoElegido] = useState(vehiculoInicial?.tipo ?? null)
  const [datos, setDatos] = useState({
    categoria_problema: '',
    categoria_otro: '',
    observacion_cliente: '',
    kilometraje: '',
    fecha_entrega_estimada: '',
  })
  const [mecanicoId, setMecanicoId] = useState(null)
  const [errores, setErrores] = useState({})
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })

  function cambiarVehiculo(nuevo) {
    // Las categorías dependen del tipo: al pasar de carro a moto se vuelve a elegir.
    if (nuevo && tipoElegido && nuevo.tipo !== tipoElegido) {
      setDatos({ ...datos, categoria_problema: '', categoria_otro: '' })
    }
    if (nuevo) setTipoElegido(nuevo.tipo)
    setVehiculo(nuevo)
  }

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setError(null)
    if (!vehiculo) {
      setErrores({ vehiculo_id: 'Busque y elija el vehículo' })
      return
    }
    if (!datos.categoria_problema) {
      setErrores({ categoria_problema: 'Elija la categoría del problema' })
      return
    }
    setGuardando(true)
    try {
      const orden = await api.post('/ordenes', {
        ...datos,
        categoria_otro: datos.categoria_problema === OTRO ? datos.categoria_otro : null,
        vehiculo_id: vehiculo.id,
        mecanico_id: mecanicoId,
      })
      navegar(`/ordenes/${orden.id}`, { state: { aviso: `Orden #${orden.numero} abierta para ${vehiculo.placa}` } })
    } catch (err) {
      setErrores(erroresPorCampo(err))
      setError(err)
      setGuardando(false)
    }
  }

  // RN-08: si el carro ya tiene una orden abierta, se ofrece ir a ella.
  const ordenAbierta = error?.status === 409 ? error.details?.orden_id : null

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-4 tarjeta p-4">
      {error && (
        <Aviso tipo="error">
          {error.message}
          {ordenAbierta && (
            <>
              {' '}
              <Link to={`/ordenes/${ordenAbierta}`} className="font-semibold underline">
                Ver la orden
              </Link>
            </>
          )}
        </Aviso>
      )}
      <SelectorVehiculo valor={vehiculo} alCambiar={cambiarVehiculo} error={errores.vehiculo_id} />
      <CamposProblema
        tipo={vehiculo?.tipo}
        datos={datos}
        alCambiar={(campo, valor) => setDatos({ ...datos, [campo]: valor })}
        errores={errores}
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <CampoFormulario
          etiqueta="Kilometraje"
          type="number"
          inputMode="numeric"
          min={0}
          value={datos.kilometraje}
          onChange={cambiar('kilometraje')}
          error={errores.kilometraje}
        />
        <CampoFormulario
          etiqueta="Entrega estimada"
          type="date"
          value={datos.fecha_entrega_estimada}
          onChange={cambiar('fecha_entrega_estimada')}
          error={errores.fecha_entrega_estimada}
        />
      </div>
      <SelectorMecanico valor={mecanicoId} alCambiar={setMecanicoId} error={errores.mecanico_id} />
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <EnlaceBoton to="/ordenes" variante="secundario">
          Cancelar
        </EnlaceBoton>
        <Boton type="submit" cargando={guardando}>
          Abrir orden
        </Boton>
      </div>
    </form>
  )
}

export default function OrdenNueva() {
  const [parametros] = useSearchParams()
  const vehiculoId = parametros.get('vehiculo')
  // Desde el detalle del carro llega ya elegido: abrir la orden toma menos pasos (RNF-02).
  const { datos, error, recargar } = useConsulta(vehiculoId ? `/vehiculos/${vehiculoId}` : null)

  let contenido
  if (error) contenido = <ErrorCarga error={error} recurso="vehiculo" alReintentar={recargar} />
  else if (vehiculoId && !datos) contenido = <Esqueleto etiqueta="Cargando carro" />
  else contenido = <Formulario vehiculoInicial={datos?.activo ? datos : null} />

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">Nueva orden</h1>
      {contenido}
    </div>
  )
}
