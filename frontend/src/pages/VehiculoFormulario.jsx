import { useState } from 'react'
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import SelectorCliente from '../components/SelectorCliente.jsx'
import { TIPOS_VEHICULO } from '../constantes.js'
import { normalizarPlaca } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'

/** Elección del tipo con dos opciones grandes (radios nativos: teclado y lector de pantalla). */
function SelectorTipo({ valor, alCambiar, error }) {
  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="mb-1 text-sm font-medium text-texto">Tipo de vehículo</legend>
      <div className="grid grid-cols-2 gap-2 sm:max-w-sm">
        {Object.entries(TIPOS_VEHICULO).map(([clave, { etiqueta, icono }]) => (
          <label
            key={clave}
            className={`flex min-h-12 cursor-pointer items-center gap-2 rounded-lg border px-3 text-sm transition-[background-color,border-color,color] duration-150 ease-salida has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-primario ${
              valor === clave
                ? 'border-primario bg-primario-suave font-semibold text-primario-oscuro'
                : 'border-borde bg-superficie font-medium text-texto-suave hover:border-texto-suave/40 hover:text-texto'
            }`}
          >
            <input
              type="radio"
              name="tipo"
              value={clave}
              checked={valor === clave}
              onChange={() => alCambiar(clave)}
              className="sr-only"
            />
            <Icono nombre={icono} />
            {etiqueta}
          </label>
        ))}
      </div>
      {error && <p className="text-sm text-peligro">{error}</p>}
    </fieldset>
  )
}

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

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })
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
      <SelectorTipo
        valor={datos.tipo}
        alCambiar={(tipo) => setDatos({ ...datos, tipo })}
        error={errores.tipo}
      />
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
          placeholder={esMoto ? 'Yamaha, AKT, Bajaj…' : 'Mazda, Chevrolet, Renault…'}
          maxLength={50}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Modelo"
          value={datos.modelo}
          onChange={cambiar('modelo')}
          error={errores.modelo}
          placeholder={esMoto ? 'FZ 2.0, NKD 125…' : '3, Spark GT, Logan…'}
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
