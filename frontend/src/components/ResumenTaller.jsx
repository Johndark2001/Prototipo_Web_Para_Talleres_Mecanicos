import { Link } from 'react-router'

import { ESTADOS_ORDEN, ROLES } from '../constantes.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useSesion } from '../sesion/contexto.js'
import Aviso from './Aviso.jsx'
import EtiquetaStock from './EtiquetaStock.jsx'
import Esqueleto from './Esqueleto.jsx'
import Icono from './Icono.jsx'

/** Dashboard mínimo (RF-14): conteos por estado y alertas de stock (RF-10). */
export default function ResumenTaller() {
  const { sesion } = useSesion()
  const esAdmin = sesion.usuario.rol === ROLES.ADMIN
  const { datos, error, recargar } = useConsulta('/dashboard')

  if (error) {
    return (
      <Aviso tipo="error">
        {error.message}{' '}
        <button type="button" onClick={recargar} className="font-semibold underline">
          Reintentar
        </button>
      </Aviso>
    )
  }
  if (!datos) return <Esqueleto filas={2} etiqueta="Cargando resumen" />

  const conteos = [
    ...Object.entries(datos.ordenes_por_estado).map(([estado, total]) => ({
      clave: estado,
      etiqueta: ESTADOS_ORDEN[estado].etiqueta,
      icono: ESTADOS_ORDEN[estado].icono,
      total,
      a: `/ordenes?filtro=${estado}`,
    })),
    {
      clave: 'ENTREGADOS_HOY',
      etiqueta: 'Entregados hoy',
      icono: 'check',
      total: datos.entregadas_hoy,
      a: '/ordenes?filtro=ENTREGADO',
    },
  ]

  return (
    <div className="flex flex-col gap-4">
      {/* Cada conteo abre la lista ya filtrada (reconocer antes que recordar). */}
      <ul aria-label="Órdenes por estado" className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {conteos.map((c) => (
          <li key={c.clave}>
            <Link
              to={c.a}
              className="flex min-h-20 flex-col justify-between rounded-lg border border-borde bg-superficie p-3 hover:border-primario"
            >
              <span className="flex items-center gap-1 text-xs font-medium text-texto-suave">
                <Icono nombre={c.icono} className="size-3.5" />
                {c.etiqueta}
              </span>
              <span className="text-2xl font-semibold">{c.total}</span>
            </Link>
          </li>
        ))}
      </ul>

      {datos.stock_bajo_total > 0 && (
        <section
          aria-labelledby="titulo-alertas"
          className="flex flex-col gap-2 rounded-lg border border-aviso/40 bg-aviso-suave p-4"
        >
          <h2 id="titulo-alertas" className="flex items-center gap-2 font-semibold text-aviso">
            <Icono nombre="alerta" className="size-5" />
            {datos.stock_bajo_total === 1
              ? '1 repuesto necesita reposición'
              : `${datos.stock_bajo_total} repuestos necesitan reposición`}
          </h2>
          <ul className="divide-y divide-aviso/20 text-sm">
            {datos.stock_bajo.map((r) => (
              <li key={r.id} className="flex items-center justify-between gap-3 py-2">
                {esAdmin ? (
                  <Link to={`/inventario/${r.id}`} className="min-w-0 truncate font-medium underline">
                    {r.nombre}
                  </Link>
                ) : (
                  <span className="min-w-0 truncate font-medium">{r.nombre}</span>
                )}
                <EtiquetaStock repuesto={r} />
              </li>
            ))}
          </ul>
          {datos.stock_bajo_total > datos.stock_bajo.length && (
            <Link to="/inventario?alertas=1" className="self-start text-sm font-semibold text-aviso underline">
              Ver todos
            </Link>
          )}
        </section>
      )}
    </div>
  )
}
