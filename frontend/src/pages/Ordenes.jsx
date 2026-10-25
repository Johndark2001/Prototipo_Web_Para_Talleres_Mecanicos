import { useSearchParams } from 'react-router'

import EnlaceBoton from '../components/EnlaceBoton.jsx'
import Icono from '../components/Icono.jsx'
import ListaOrdenes from '../components/ListaOrdenes.jsx'
import { ESTADOS_ORDEN, ROLES, ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'

// "abiertas" es el filtro por defecto: es lo que el taller tiene entre manos.
const FILTROS = [
  { valor: 'abiertas', etiqueta: 'Abiertas' },
  ...Object.entries(ESTADOS_ORDEN).map(([valor, { etiqueta }]) => ({ valor, etiqueta })),
  { valor: 'todas', etiqueta: 'Todas' },
]

function filtrosApi(filtro) {
  if (filtro === 'abiertas') return { abiertas: true }
  if (filtro === 'todas') return {}
  return { estado: filtro }
}

export default function Ordenes() {
  const { sesion } = useSesion()
  const esMecanico = sesion.usuario.rol === ROLES.MECANICO
  const puedeAbrir = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol)
  const [parametros, setParametros] = useSearchParams()
  const filtro = parametros.get('filtro') ?? 'abiertas'

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{esMecanico ? 'Mis órdenes' : 'Órdenes de trabajo'}</h1>
          <p className="text-sm text-texto-suave">
            {esMecanico ? 'Los carros que le asignaron.' : 'Los carros que entraron al taller.'}
          </p>
        </div>
        {puedeAbrir && (
          <EnlaceBoton to="/ordenes/nueva">
            <Icono nombre="mas" />
            Nueva orden
          </EnlaceBoton>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="filtro-estado" className="text-sm font-medium">
          Mostrar
        </label>
        <select
          id="filtro-estado"
          value={filtro}
          onChange={(e) => setParametros(e.target.value === 'abiertas' ? {} : { filtro: e.target.value }, { replace: true })}
          className="min-h-11 rounded-md border border-borde bg-superficie px-3 text-base sm:max-w-xs sm:text-sm"
        >
          {FILTROS.map((f) => (
            <option key={f.valor} value={f.valor}>
              {f.etiqueta}
            </option>
          ))}
        </select>
      </div>

      <ListaOrdenes
        filtros={filtrosApi(filtro)}
        vacio={
          esMecanico
            ? {
                titulo: 'No tiene órdenes en esta lista',
                texto: 'Cuando le asignen un carro, aparecerá aquí para que registre el diagnóstico y el trabajo.',
              }
            : {
                titulo: 'No hay órdenes en esta lista',
                texto: puedeAbrir ? 'Para recibir un carro use «Nueva orden».' : undefined,
              }
        }
      />
    </div>
  )
}
