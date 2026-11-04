import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import { conParametros } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import EtiquetaStock from '../components/EtiquetaStock.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import Paginacion from '../components/Paginacion.jsx'
import { ROLES } from '../constantes.js'
import { formatearCantidad, formatearPesos } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useRetrasado } from '../hooks/useRetrasado.js'
import { useSesion } from '../sesion/contexto.js'

const TAMANO_PAGINA = 20

function ContenidoFila({ repuesto }) {
  return (
    <>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{repuesto.nombre}</p>
        <p className="truncate text-sm text-texto-suave">
          <span className="font-mono">{repuesto.codigo}</span> · {formatearPesos(repuesto.precio_venta)} /{' '}
          {repuesto.unidad} · mínimo {formatearCantidad(repuesto.stock_minimo)}
        </p>
      </div>
      <div className="flex flex-col items-end gap-1">
        <EtiquetaStock repuesto={repuesto} />
        {!repuesto.activo && <EtiquetaActivo activo={false} />}
      </div>
    </>
  )
}

function FilaRepuesto({ repuesto, enlazar }) {
  // Solo el ADMIN entra al detalle: allí se mueve el stock (SPEC §3).
  return (
    <li>
      {enlazar ? (
        <Link to={`/inventario/${repuesto.id}`} className="flex min-h-14 items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-fondo">
          <ContenidoFila repuesto={repuesto} />
          <Icono nombre="derecha" className="size-5 shrink-0 text-texto-suave" />
        </Link>
      ) : (
        <div className="flex min-h-14 items-center gap-3 px-4 py-3">
          <ContenidoFila repuesto={repuesto} />
        </div>
      )}
    </li>
  )
}

export default function Inventario() {
  const { sesion } = useSesion()
  const esAdmin = sesion.usuario.rol === ROLES.ADMIN
  const [parametros, setParametros] = useSearchParams()
  const [texto, setTexto] = useState(parametros.get('buscar') ?? '')
  const busqueda = useRetrasado(texto.trim())
  const soloBajos = parametros.get('alertas') === '1'
  const verInactivos = parametros.get('inactivos') === '1'
  const pagina = Number(parametros.get('pagina') ?? 1)

  const { datos, error, recargar } = useConsulta(
    conParametros('/repuestos', {
      buscar: busqueda,
      stock_bajo: soloBajos ? true : undefined,
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

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Inventario</h1>
        {esAdmin && (
          <EnlaceBoton to="/inventario/nuevo">
            <Icono nombre="mas" />
            Repuesto
          </EnlaceBoton>
        )}
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <label htmlFor="buscar-repuesto" className="sr-only">
          Buscar repuesto
        </label>
        <input
          id="buscar-repuesto"
          type="search"
          value={texto}
          onChange={(e) => {
            setTexto(e.target.value)
            cambiarParametros({ buscar: e.target.value.trim(), pagina: null })
          }}
          placeholder="Nombre o código, p. ej. filtro o W712"
          autoComplete="off"
          maxLength={60}
          className="min-h-11 w-full rounded-lg border border-borde bg-superficie px-3 text-base sm:max-w-md sm:text-sm"
        />
        <label className="inline-flex min-h-11 items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={soloBajos}
            onChange={(e) => cambiarParametros({ alertas: e.target.checked ? '1' : null, pagina: null })}
            className="size-4"
          />
          Solo con stock bajo
        </label>
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

      {!datos && !error && <Esqueleto etiqueta="Cargando inventario" />}

      {datos?.data.length === 0 &&
        (busqueda || soloBajos ? (
          <EstadoVacio
            icono="buscar"
            titulo={soloBajos && !busqueda ? 'Ningún repuesto está en el mínimo' : `No hay repuestos con «${busqueda}»`}
          />
        ) : (
          <EstadoVacio
            icono="caja"
            titulo="Aún no hay repuestos registrados"
            texto={
              esAdmin
                ? 'Registre los repuestos que vende el taller con su precio y el stock que tiene en el estante.'
                : 'Pídale al administrador que registre los repuestos del taller.'
            }
          />
        ))}

      {datos?.data.length > 0 && (
        <ul className="divide-y divide-borde tarjeta">
          {datos.data.map((repuesto) => (
            <FilaRepuesto key={repuesto.id} repuesto={repuesto} enlazar={esAdmin} />
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
