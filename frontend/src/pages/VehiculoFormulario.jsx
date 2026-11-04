import { useState } from 'react'
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CamposVehiculo from '../components/CamposVehiculo.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import SelectorCliente from '../components/SelectorCliente.jsx'
import { TIPOS_VEHICULO } from '../constantes.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'

function Formulario({ inicial, duenoInicial }) {
  const navegar = useNavigate()
  const esNuevo = !inicial.id
  const [datos, setDatos] = useState({
    placa: inicial.placa ?? '',
    tipo: TIPOS_VEHICULO[inicial.tipo] ? inicial.tipo : 'CARRO',
    marca: inicial.marca ?? '',
    modelo: inicial.modelo ?? '',
    anio: inicial.anio ?? '',
    color: inicial.color ?? '',
  })
  const [dueno, setDueno] = useState(duenoInicial)
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambioDeDueno = !esNuevo && dueno && dueno.id !== duenoInicial?.id
  const esMoto = datos.tipo === 'MOTO'
  const nombreTipo = TIPOS_VEHICULO[datos.tipo].etiqueta

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    if (!dueno) {
      setErrores({ cliente_id: `Elija el dueño de${esMoto ? ' la moto' : 'l carro'}` })
      return
    }
    setGuardando(true)
    const cuerpo = { ...datos, anio: datos.anio === '' ? null : Number(datos.anio), cliente_id: dueno.id }
    try {
      const guardado = esNuevo
        ? await api.post('/vehiculos', cuerpo)
        : await api.patch(`/vehiculos/${inicial.id}`, cuerpo)
      navegar(`/vehiculos/${guardado.id}`, {
        state: {
          aviso: esNuevo
            ? `${nombreTipo} ${guardado.placa} ${esMoto ? 'registrada' : 'registrado'}`
            : 'Cambios guardados',
        },
      })
    } catch (err) {
      setErrores(erroresPorCampo(err))
      setErrorGeneral(err.message)
      setGuardando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="tarjeta flex flex-col gap-4 p-4 sm:p-6">
      {errorGeneral && <Aviso tipo="error">{errorGeneral}</Aviso>}
      <CamposVehiculo datos={datos} alCambiar={setDatos} errores={errores} />

      <SelectorCliente
        valor={dueno}
        alCambiar={setDueno}
        error={errores.cliente_id}
        enlaceNuevo={esNuevo ? '/clientes/nuevo' : undefined}
        estadoNuevo={{ vehiculo: datos }}
        ayuda={
          esNuevo
            ? undefined
            : 'Cambie el dueño solo si el vehículo se vendió. Las órdenes anteriores conservan a su dueño de entonces.'
        }
      />
      {cambioDeDueno && (
        <Aviso tipo="info">
          Al guardar, el vehículo pasará de {duenoInicial.nombre} a {dueno.nombre}.
        </Aviso>
      )}

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <EnlaceBoton to={esNuevo ? '/vehiculos' : `/vehiculos/${inicial.id}`} variante="secundario">
          Cancelar
        </EnlaceBoton>
        <Boton type="submit" cargando={guardando}>
          {esNuevo ? `Guardar ${nombreTipo.toLowerCase()}` : 'Guardar cambios'}
        </Boton>
      </div>
    </form>
  )
}

export default function VehiculoFormulario() {
  const { id } = useParams()
  const [parametros] = useSearchParams()
  const ubicacion = useLocation()
  const [aviso, setAviso] = useAvisoNavegacion()
  const clienteId = parametros.get('cliente')
  // Al editar se carga el carro (trae a su dueño); al crear desde un cliente, se carga el cliente.
  const ruta = id ? `/vehiculos/${id}` : clienteId ? `/clientes/${clienteId}` : null
  const { datos, error, recargar } = useConsulta(ruta)

  let contenido
  if (error) {
    contenido = <ErrorCarga error={error} recurso={id ? 'vehiculo' : 'cliente'} alReintentar={recargar} />
  } else if (ruta && !datos) {
    contenido = <Esqueleto etiqueta="Cargando" />
  } else if (id) {
    contenido = <Formulario key={datos.id} inicial={datos} duenoInicial={datos.cliente} />
  } else {
    const dueno = datos?.activo ? datos : null
    contenido = (
      <Formulario inicial={{ placa: ubicacion.state?.placa, tipo: ubicacion.state?.tipo }} duenoInicial={dueno} />
    )
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">
        {id ? `Editar vehículo${datos?.placa ? ` ${datos.placa}` : ''}` : 'Nuevo vehículo'}
      </h1>
      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}
      {contenido}
    </div>
  )
}
