import { useId, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import CamposVehiculo from '../components/CamposVehiculo.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import { VEHICULO_VACIO } from '../constantes.js'
import { formatearFecha, normalizarPlaca } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'

const VACIO = { nombre: '', telefono: '', email: '', documento: '', autoriza_datos: false }

function CasillaAutorizacion({ marcada, alCambiar, error }) {
  const id = useId()
  return (
    <div className="flex flex-col gap-1 rounded-lg border border-borde bg-fondo p-3">
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

/** Errores del alta conjunta: «vehiculo.placa» → { placa } para los campos del vehículo. */
function separarErrores(errores) {
  const cliente = {}
  const vehiculo = {}
  for (const [campo, mensaje] of Object.entries(errores)) {
    if (campo.startsWith('vehiculo.')) vehiculo[campo.slice('vehiculo.'.length)] = mensaje
    else cliente[campo] = mensaje
  }
  return { cliente, vehiculo }
}

function Formulario({ inicial, vehiculoInicial }) {
  const navegar = useNavigate()
  const esNuevo = !inicial.id
  const [datos, setDatos] = useState({
    ...VACIO,
    ...inicial,
    email: inicial.email ?? '',
    documento: inicial.documento ?? '',
  })
  // Cambio #6: el primer vehículo se registra con el cliente, en la misma operación.
  const [vehiculo, setVehiculo] = useState({ ...VEHICULO_VACIO, ...vehiculoInicial })
  const [sinVehiculo, setSinVehiculo] = useState(false)
  const [errores, setErrores] = useState({})
  const [erroresVehiculo, setErroresVehiculo] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const conVehiculo = esNuevo && !sinVehiculo

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })
  const volverA = esNuevo ? '/clientes' : `/clientes/${inicial.id}`

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErroresVehiculo({})
    setErrorGeneral(null)
    setGuardando(true)
    const { nombre, telefono, email, documento } = datos
    const cuerpoVehiculo = conVehiculo
      ? { ...vehiculo, anio: vehiculo.anio === '' ? null : Number(vehiculo.anio) }
      : null
    try {
      const guardado = esNuevo
        ? await api.post('/clientes', {
            nombre,
            telefono,
            email,
            documento,
            autoriza_datos: datos.autoriza_datos,
            vehiculo: cuerpoVehiculo,
          })
        : await api.patch(`/clientes/${inicial.id}`, { nombre, telefono, email, documento })
      if (!esNuevo) {
        navegar(`/clientes/${guardado.id}`, { state: { aviso: 'Cambios guardados' } })
        return
      }
      // Se confirma con la respuesta del servidor, no con lo que se envió: si el vehículo no
      // vuelve asociado al cliente, se avisa en vez de mostrar un éxito falso.
      const placa = cuerpoVehiculo && normalizarPlaca(cuerpoVehiculo.placa)
      const asociado = !placa || guardado.vehiculos?.some((v) => v.placa === placa)
      navegar(`/clientes/${guardado.id}`, {
        state: asociado
          ? {
              aviso: placa
                ? `Cliente ${guardado.nombre} registrado con el vehículo ${placa}`
                : `Cliente ${guardado.nombre} registrado`,
            }
          : {
              avisoTipo: 'error',
              aviso: `El cliente ${guardado.nombre} se guardó, pero el servidor no registró el vehículo ${placa}. Agréguelo con «Agregar vehículo» y avise al administrador del sistema.`,
            },
      })
    } catch (err) {
      const separados = separarErrores(erroresPorCampo(err))
      setErrores(separados.cliente)
      setErroresVehiculo(separados.vehiculo)
      setErrorGeneral(err.message)
      setGuardando(false)
    }
  }

  return (
    <form
      onSubmit={enviar}
      noValidate
      className="flex flex-col gap-4 tarjeta p-4"
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

      <details className="group rounded-lg border border-borde" open={Boolean(inicial.email || inicial.documento)}>
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

      {esNuevo && (
        <section aria-labelledby="titulo-vehiculo" className="flex flex-col gap-4 border-t border-borde pt-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 id="titulo-vehiculo" className="flex items-center gap-2 text-base font-semibold">
              <Icono nombre={vehiculo.tipo === 'MOTO' ? 'moto' : 'carro'} className="size-5 text-texto-suave" />
              Información del vehículo
            </h2>
            <label className="inline-flex min-h-11 items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={sinVehiculo}
                onChange={(e) => setSinVehiculo(e.target.checked)}
                className="size-4"
              />
              Registrar sin vehículo por ahora
            </label>
          </div>
          {conVehiculo ? (
            <CamposVehiculo datos={vehiculo} alCambiar={setVehiculo} errores={erroresVehiculo} />
          ) : (
            <p className="text-sm text-texto-suave">
              Podrá agregar sus vehículos después, desde la ficha del cliente.
            </p>
          )}
        </section>
      )}

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
        <EnlaceBoton to={volverA} variante="secundario">
          Cancelar
        </EnlaceBoton>
        <Boton type="submit" cargando={guardando}>
          {esNuevo ? 'Guardar cliente' : 'Guardar cambios'}
        </Boton>
      </div>
    </form>
  )
}

export default function ClienteFormulario() {
  const { id } = useParams()
  // Desde el formulario del vehículo llegan los datos que ya se habían escrito.
  const { state } = useLocation()
  const { datos, error, recargar } = useConsulta(id ? `/clientes/${id}` : null)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">
        {id ? `Editar cliente${datos ? `: ${datos.nombre}` : ''}` : 'Nuevo cliente'}
      </h1>
      {!id && <Formulario inicial={{}} vehiculoInicial={state?.vehiculo} />}
      {id && error && <ErrorCarga error={error} recurso="cliente" alReintentar={recargar} />}
      {id && !datos && !error && <Esqueleto etiqueta="Cargando cliente" />}
      {id && datos && <Formulario key={datos.id} inicial={datos} />}
    </div>
  )
}
