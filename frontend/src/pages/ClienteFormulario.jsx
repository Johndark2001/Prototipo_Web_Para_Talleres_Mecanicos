import { useId, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import { formatearFecha } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'

const VACIO = { nombre: '', telefono: '', email: '', documento: '', autoriza_datos: false }

function CasillaAutorizacion({ marcada, alCambiar, error }) {
  const id = useId()
  return (
    <div className="flex flex-col gap-1 rounded-md border border-borde bg-fondo p-3">
      <label htmlFor={id} className="flex items-start gap-3 text-sm">
        <input
          id={id}
          type="checkbox"
          checked={marcada}
          onChange={(e) => alCambiar(e.target.checked)}
          aria-invalid={Boolean(error)}
          aria-describedby={`${id}-ayuda${error ? ` ${id}-error` : ''}`}
          className="mt-0.5 size-5 shrink-0"
          required
        />
        <span>
          El cliente autoriza el tratamiento de sus datos personales (Ley 1581 de 2012)
          <span className="text-peligro" aria-hidden="true">
            {' '}
            *
          </span>
        </span>
      </label>
      <p id={`${id}-ayuda`} className="text-xs text-texto-suave">
        Pregúntele antes de marcar. Sus datos solo se usan para atender su carro.
      </p>
      {error && (
        <p id={`${id}-error`} className="text-sm text-peligro">
          {error}
        </p>
      )}
    </div>
  )
}

function Formulario({ inicial }) {
  const navegar = useNavigate()
  const [parametros] = useSearchParams()
  const esNuevo = !inicial.id
  const [datos, setDatos] = useState({
    ...VACIO,
    ...inicial,
    email: inicial.email ?? '',
    documento: inicial.documento ?? '',
  })
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })
  const volverA = esNuevo ? '/clientes' : `/clientes/${inicial.id}`

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    setGuardando(true)
    const { nombre, telefono, email, documento } = datos
    try {
      const guardado = esNuevo
        ? await api.post('/clientes', { nombre, telefono, email, documento, autoriza_datos: datos.autoriza_datos })
        : await api.patch(`/clientes/${inicial.id}`, { nombre, telefono, email, documento })
      // Desde el formulario de carro se vuelve a él con el dueño ya elegido (flujo de recepción).
      if (esNuevo && parametros.get('siguiente') === 'vehiculo') {
        navegar(`/vehiculos/nuevo?cliente=${guardado.id}`, {
          state: { aviso: `Cliente ${guardado.nombre} registrado. Ahora registre su carro.` },
        })
        return
      }
      navegar(`/clientes/${guardado.id}`, {
        state: { aviso: esNuevo ? `Cliente ${guardado.nombre} registrado` : 'Cambios guardados' },
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
          etiqueta="Nombre"
          value={datos.nombre}
          onChange={cambiar('nombre')}
          error={errores.nombre}
          autoComplete="off"
          obligatorio
        />
        <CampoFormulario
          etiqueta="Teléfono"
          type="tel"
          inputMode="tel"
          value={datos.telefono}
          onChange={cambiar('telefono')}
          error={errores.telefono}
          ayuda="Celular o fijo. Puede escribirlo con espacios."
          autoComplete="off"
          obligatorio
        />
      </div>

      <details className="group rounded-md border border-borde" open={Boolean(inicial.email || inicial.documento)}>
        <summary className="flex min-h-11 cursor-pointer items-center gap-2 px-3 text-sm font-medium">
          <Icono nombre="derecha" className="size-4 transition-transform group-open:rotate-90" />
          Más datos (opcional)
        </summary>
        <div className="grid gap-4 p-3 pt-0 sm:grid-cols-2">
          <CampoFormulario
            etiqueta="Correo"
            type="email"
            inputMode="email"
            value={datos.email}
            onChange={cambiar('email')}
            error={errores.email}
            autoComplete="off"
          />
          <CampoFormulario
            etiqueta="Documento"
            value={datos.documento}
            onChange={cambiar('documento')}
            error={errores.documento}
            ayuda="Cédula o NIT. Pídalo solo si el cliente lo quiere dar."
            autoComplete="off"
          />
        </div>
      </details>

      {esNuevo ? (
        <CasillaAutorizacion
          marcada={datos.autoriza_datos}
          alCambiar={(valor) => setDatos({ ...datos, autoriza_datos: valor })}
          error={errores.autoriza_datos}
        />
      ) : (
        <p className="flex items-center gap-2 text-sm text-texto-suave">
          <Icono nombre="check" className="size-4 text-exito" />
          Autorizó el tratamiento de datos el {formatearFecha(inicial.fecha_autorizacion)}.
        </p>
      )}

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Link
          to={volverA}
          className="inline-flex min-h-11 items-center justify-center rounded-md border border-borde px-4 text-sm font-semibold hover:bg-fondo"
        >
          Cancelar
        </Link>
        <Boton type="submit" cargando={guardando}>
          {esNuevo ? 'Guardar cliente' : 'Guardar cambios'}
        </Boton>
      </div>
    </form>
  )
}

export default function ClienteFormulario() {
  const { id } = useParams()
  const { datos, error, recargar } = useConsulta(id ? `/clientes/${id}` : null)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">
        {id ? `Editar cliente${datos ? `: ${datos.nombre}` : ''}` : 'Nuevo cliente'}
      </h1>
      {!id && <Formulario inicial={{}} />}
      {id && error && <ErrorCarga error={error} recurso="cliente" alReintentar={recargar} />}
      {id && !datos && !error && <Esqueleto etiqueta="Cargando cliente" />}
      {id && datos && <Formulario key={datos.id} inicial={datos} />}
    </div>
  )
}
