import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import { conParametros } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import Paginacion from '../components/Paginacion.jsx'
import { ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { formatearTelefono } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useRetrasado } from '../hooks/useRetrasado.js'
import { useSesion } from '../sesion/contexto.js'

const TAMANO_PAGINA = 20

function FilaCliente({ cliente }) {
  const carros = cliente.total_vehiculos
  return (
    <li>
      <Link
        to={`/clientes/${cliente.id}`}
        className="flex min-h-14 items-center gap-3 px-4 py-3 hover:bg-fondo"
      >
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium">{cliente.nombre}</p>
          <p className="truncate text-sm text-texto-suave">
            {formatearTelefono(cliente.telefono)} · {carros} {carros === 1 ? 'carro' : 'carros'}
          </p>
        </div>
        {!cliente.activo && <EtiquetaActivo activo={false} />}
        <Icono nombre="derecha" className="size-5 shrink-0 text-texto-suave" />
      </Link>
    </li>
  )
}

export default function Clientes() {
  const { sesion } = useSesion()
  const puedeEditar = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol)
  const [parametros, setParametros] = useSearchParams()
  const [texto, setTexto] = useState(parametros.get('q') ?? '')
  const busqueda = useRetrasado(texto.trim())
  const verInactivos = parametros.get('inactivos') === '1'
  const pagina = Number(parametros.get('pagina') ?? 1)

  const { datos, error, recargar } = useConsulta(
    conParametros('/clientes', {
      q: busqueda,
      activo: verInactivos ? undefined : true,
      page: pagina,
      page_size: TAMANO_PAGINA,
    }),
  )

  function cambiarParametros(cambios) {
    const nuevos = new URLSearchParams(parametros)
    for (const [clave, valor] of Object.entries(cambios)) {
      if (valor) nuevos.set(clave, valor)
      else nuevos.delete(clave)
    }
    setParametros(nuevos, { replace: true })
  }

  function escribir(evento) {
    setTexto(evento.target.value)
    cambiarParametros({ q: evento.target.value.trim(), pagina: null })
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Clientes</h1>
          <p className="text-sm text-texto-suave">Dueños de los carros que atiende el taller.</p>
        </div>
        {puedeEditar && (
          <Link
            to="/clientes/nuevo"
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-primario px-4 text-sm font-semibold text-white hover:bg-primario-oscuro"
          >
            <Icono nombre="mas" />
            Cliente
          </Link>
        )}
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <label htmlFor="buscar-cliente" className="sr-only">
          Buscar cliente
        </label>
        <input
          id="buscar-cliente"
          type="search"
          value={texto}
          onChange={escribir}
          placeholder="Buscar por nombre, teléfono o documento"
          autoComplete="off"
          className="min-h-11 w-full rounded-md border border-borde bg-superficie px-3 text-base sm:max-w-md sm:text-sm"
        />
        <label className="inline-flex min-h-11 items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={verInactivos}
            onChange={(e) => cambiarParametros({ inactivos: e.target.checked ? '1' : null, pagina: null })}
            className="size-4"
          />
          Incluir inactivos
        </label>
      </div>

      {error && (
        <Aviso tipo="error">
          {error.message}{' '}
          <button type="button" onClick={recargar} className="font-semibold underline">
            Reintentar
          </button>
        </Aviso>
      )}

      {!datos && !error && <Esqueleto etiqueta="Cargando clientes" />}

      {datos?.data.length === 0 &&
        (busqueda ? (
          <EstadoVacio
            icono="buscar"
            titulo="No se encontraron clientes"
            texto={`Ningún cliente coincide con «${busqueda}». Revise lo que escribió o registre al cliente.`}
          />
        ) : (
          <EstadoVacio
            icono="cliente"
            titulo="Aún no hay clientes registrados"
            texto={
              puedeEditar
                ? 'Registre al primer cliente con el botón «+ Cliente». Necesitará su autorización de datos.'
                : 'Cuando recepción registre clientes, aparecerán aquí.'
            }
          />
        ))}

      {datos?.data.length > 0 && (
        <ul className="divide-y divide-borde rounded-lg border border-borde bg-superficie">
          {datos.data.map((cliente) => (
            <FilaCliente key={cliente.id} cliente={cliente} />
          ))}
        </ul>
      )}

      <Paginacion
        paginacion={datos?.pagination}
        alCambiar={(nueva) => cambiarParametros({ pagina: nueva > 1 ? String(nueva) : null })}
      />
    </div>
  )
}
