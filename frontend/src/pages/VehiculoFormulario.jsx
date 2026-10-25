import { useState } from 'react'
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import SelectorCliente from '../components/SelectorCliente.jsx'
import { normalizarPlaca } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'

function Formulario({ inicial, duenoInicial }) {
  const navegar = useNavigate()
  const esNuevo = !inicial.id
  const [datos, setDatos] = useState({
    placa: inicial.placa ?? '',
    marca: inicial.marca ?? '',
    modelo: inicial.modelo ?? '',
    anio: inicial.anio ?? '',
    color: inicial.color ?? '',
  })
  const [dueno, setDueno] = useState(duenoInicial)
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })
  const cambioDeDueno = !esNuevo && dueno && dueno.id !== duenoInicial?.id

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    if (!dueno) {
      setErrores({ cliente_id: 'Elija el dueño del carro' })
      return
    }
    setGuardando(true)
    const cuerpo = { ...datos, anio: datos.anio === '' ? null : Number(datos.anio), cliente_id: dueno.id }
    try {
      const guardado = esNuevo
        ? await api.post('/vehiculos', cuerpo)
        : await api.patch(`/vehiculos/${inicial.id}`, cuerpo)
      navegar(`/vehiculos/${guardado.id}`, {
        state: { aviso: esNuevo ? `Carro ${guardado.placa} registrado` : 'Cambios guardados' },
      })
    } catch (err) {
      setErrores(erroresPorCampo(err))
      setErrorGeneral(err.message)
      setGuardando(false)
    }
  }

  return (
    <form
      onSubmit={enviar}
      noValidate
      className="flex flex-col gap-4 rounded-lg border border-borde bg-superficie p-4"
    >
      {errorGeneral && <Aviso tipo="error">{errorGeneral}</Aviso>}
      <div className="grid gap-4 sm:grid-cols-2">
        <CampoFormulario
          etiqueta="Placa"
          value={datos.placa}
          onChange={(e) => setDatos({ ...datos, placa: e.target.value.toUpperCase() })}
          onBlur={() => setDatos({ ...datos, placa: normalizarPlaca(datos.placa) })}
          error={errores.placa}
          ayuda="Sin espacios ni guiones. Se corrige sola al salir del campo."
          autoCapitalize="characters"
          autoComplete="off"
          maxLength={12}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Marca"
          value={datos.marca}
          onChange={cambiar('marca')}
          error={errores.marca}
          placeholder="Mazda, Chevrolet, Yamaha…"
          maxLength={50}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Modelo"
          value={datos.modelo}
          onChange={cambiar('modelo')}
          error={errores.modelo}
          placeholder="3, Spark GT, FZ…"
          maxLength={50}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Año"
          type="number"
          inputMode="numeric"
          min={1950}
          max={2100}
          value={datos.anio}
          onChange={cambiar('anio')}
          error={errores.anio}
        />
        <CampoFormulario
          etiqueta="Color"
          value={datos.color}
          onChange={cambiar('color')}
          error={errores.color}
          maxLength={30}
        />
      </div>

      <SelectorCliente
        valor={dueno}
        alCambiar={setDueno}
        error={errores.cliente_id}
        enlaceNuevo={esNuevo ? '/clientes/nuevo?siguiente=vehiculo' : undefined}
        ayuda={
          esNuevo
            ? undefined
            : 'Cambie el dueño solo si el carro se vendió. Las órdenes anteriores conservan a su dueño de entonces.'
        }
      />
      {cambioDeDueno && (
        <Aviso tipo="info">
          Al guardar, el carro pasará de {duenoInicial.nombre} a {dueno.nombre}.
        </Aviso>
      )}

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <EnlaceBoton to={esNuevo ? '/vehiculos' : `/vehiculos/${inicial.id}`} variante="secundario">
          Cancelar
        </EnlaceBoton>
        <Boton type="submit" cargando={guardando}>
          {esNuevo ? 'Guardar carro' : 'Guardar cambios'}
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
    contenido = <Formulario inicial={{ placa: ubicacion.state?.placa }} duenoInicial={dueno} />
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">
        {id ? `Editar carro${datos?.placa ? ` ${datos.placa}` : ''}` : 'Nuevo carro'}
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
