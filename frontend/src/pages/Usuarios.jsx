import { useCallback, useEffect, useState } from 'react'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import DialogoConfirmacion from '../components/DialogoConfirmacion.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import { ETIQUETAS_ROL, ROLES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'

const TAMANO_PAGINA = 20
const FORMULARIO_VACIO = { nombre: '', email: '', password: '', rol: ROLES.MECANICO }

function FormularioUsuario({ alGuardar, alCancelar }) {
  const [datos, setDatos] = useState(FORMULARIO_VACIO)
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    setGuardando(true)
    try {
      const creado = await api.post('/usuarios', datos)
      alGuardar(creado)
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
      aria-labelledby="titulo-nuevo-usuario"
    >
      <h2 id="titulo-nuevo-usuario" className="text-base font-semibold">
        Nuevo usuario
      </h2>
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
          etiqueta="Correo"
          type="email"
          inputMode="email"
          value={datos.email}
          onChange={cambiar('email')}
          error={errores.email}
          autoComplete="off"
          obligatorio
        />
        <CampoFormulario
          etiqueta="Clave inicial"
          type="password"
          value={datos.password}
          onChange={cambiar('password')}
          error={errores.password}
          ayuda="Mínimo 8 caracteres. Entréguela a la persona en privado."
          autoComplete="new-password"
          obligatorio
        />
        <CampoFormulario etiqueta="Rol" error={errores.rol} obligatorio>
          {(propsCampo) => (
            <select {...propsCampo} value={datos.rol} onChange={cambiar('rol')}>
              {Object.values(ROLES).map((rol) => (
                <option key={rol} value={rol}>
                  {ETIQUETAS_ROL[rol]}
                </option>
              ))}
            </select>
          )}
        </CampoFormulario>
      </div>
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Boton variante="secundario" onClick={alCancelar} disabled={guardando}>
          Cancelar
        </Boton>
        <Boton type="submit" cargando={guardando}>
          Guardar usuario
        </Boton>
      </div>
    </form>
  )
}

function FilaUsuario({ usuario, esUsted, alCambiarRol, alCambiarActivo }) {
  return (
    <li className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">
          {usuario.nombre}
          {esUsted && <span className="ml-2 text-xs font-normal text-texto-suave">(usted)</span>}
        </p>
        <p className="truncate text-sm text-texto-suave">{usuario.email}</p>
      </div>
      <div className="flex items-center gap-2">
        <label className="sr-only" htmlFor={`rol-${usuario.id}`}>
          Rol de {usuario.nombre}
        </label>
        <select
          id={`rol-${usuario.id}`}
          value={usuario.rol}
          disabled={esUsted || !usuario.activo}
          onChange={(e) => alCambiarRol(usuario, e.target.value)}
          className="min-h-11 rounded-md border border-borde bg-superficie px-2 text-sm disabled:opacity-60"
        >
          {Object.values(ROLES).map((rol) => (
            <option key={rol} value={rol}>
              {ETIQUETAS_ROL[rol]}
            </option>
          ))}
        </select>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${
            usuario.activo ? 'bg-exito-suave text-exito' : 'bg-fondo text-texto-suave'
          }`}
        >
          <Icono nombre={usuario.activo ? 'check' : 'candado'} className="size-3.5" />
          {usuario.activo ? 'Activo' : 'Inactivo'}
        </span>
        {!esUsted && (
          <Boton variante="texto" onClick={() => alCambiarActivo(usuario)}>
            {usuario.activo ? 'Desactivar' : 'Activar'}
          </Boton>
        )}
      </div>
    </li>
  )
}

export default function Usuarios() {
  const { sesion } = useSesion()
  const [pagina, setPagina] = useState(1)
  const [resultado, setResultado] = useState(null)
  const [errorCarga, setErrorCarga] = useState(null)
  const [creando, setCreando] = useState(false)
  const [aviso, setAviso] = useState(null)
  const [porConfirmar, setPorConfirmar] = useState(null)
  const [confirmando, setConfirmando] = useState(false)

  const cargar = useCallback(
    () =>
      api
        .get(`/usuarios?page=${pagina}&page_size=${TAMANO_PAGINA}`)
        .then((datos) => {
          setResultado(datos)
          setErrorCarga(null)
        })
        .catch((err) => setErrorCarga(err.message)),
    [pagina],
  )

  useEffect(() => {
    cargar()
  }, [cargar])

  async function actualizar(usuario, cambios, mensajeExito) {
    try {
      await api.patch(`/usuarios/${usuario.id}`, cambios)
      setAviso({ tipo: 'exito', texto: mensajeExito })
      await cargar()
    } catch (err) {
      setAviso({ tipo: 'error', texto: err.message })
    }
  }

  async function confirmarCambioActivo() {
    const usuario = porConfirmar
    setConfirmando(true)
    await actualizar(
      usuario,
      { activo: !usuario.activo },
      `${usuario.nombre} quedó ${usuario.activo ? 'inactivo' : 'activo'}`,
    )
    setConfirmando(false)
    setPorConfirmar(null)
  }

  const paginacion = resultado?.pagination

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Usuarios del taller</h1>
          <p className="text-sm text-texto-suave">
            Cada persona entra con su propio correo y clave.
          </p>
        </div>
        {!creando && (
          <Boton onClick={() => setCreando(true)}>
            <Icono nombre="mas" />
            Usuario
          </Boton>
        )}
      </div>

      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}

      {creando && (
        <FormularioUsuario
          alCancelar={() => setCreando(false)}
          alGuardar={(creado) => {
            setCreando(false)
            setAviso({ tipo: 'exito', texto: `Usuario ${creado.nombre} creado` })
            cargar()
          }}
        />
      )}

      {errorCarga && (
        <Aviso tipo="error">
          {errorCarga}{' '}
          <button type="button" onClick={cargar} className="font-semibold underline">
            Reintentar
          </button>
        </Aviso>
      )}

      {!resultado && !errorCarga && <Esqueleto etiqueta="Cargando usuarios" />}

      {resultado && resultado.data.length === 0 && (
        <EstadoVacio icono="usuarios" titulo="No hay usuarios en esta página" />
      )}

      {resultado && resultado.data.length > 0 && (
        <ul className="divide-y divide-borde rounded-lg border border-borde bg-superficie">
          {resultado.data.map((usuario) => (
            <FilaUsuario
              key={usuario.id}
              usuario={usuario}
              esUsted={usuario.id === sesion.usuario.id}
              alCambiarRol={(u, rol) =>
                actualizar(u, { rol }, `${u.nombre} ahora es ${ETIQUETAS_ROL[rol]}`)
              }
              alCambiarActivo={setPorConfirmar}
            />
          ))}
        </ul>
      )}

      {paginacion && paginacion.total_pages > 1 && (
        <nav aria-label="Paginación" className="flex items-center justify-between gap-2">
          <Boton
            variante="secundario"
            disabled={paginacion.page <= 1}
            onClick={() => setPagina((p) => p - 1)}
          >
            Anterior
          </Boton>
          <span className="text-sm text-texto-suave">
            Página {paginacion.page} de {paginacion.total_pages}
          </span>
          <Boton
            variante="secundario"
            disabled={paginacion.page >= paginacion.total_pages}
            onClick={() => setPagina((p) => p + 1)}
          >
            Siguiente
          </Boton>
        </nav>
      )}

      <DialogoConfirmacion
        abierto={Boolean(porConfirmar)}
        titulo={porConfirmar?.activo ? '¿Desactivar este usuario?' : '¿Activar este usuario?'}
        mensaje={
          porConfirmar?.activo
            ? `${porConfirmar.nombre} perderá el acceso de inmediato. Su historial se conserva.`
            : `${porConfirmar?.nombre} podrá volver a ingresar al sistema.`
        }
        textoConfirmar={porConfirmar?.activo ? 'Desactivar' : 'Activar'}
        variante={porConfirmar?.activo ? 'peligro' : 'primario'}
        cargando={confirmando}
        alConfirmar={confirmarCambioActivo}
        alCancelar={() => setPorConfirmar(null)}
      />
    </div>
  )
}
