import EnlaceBoton from '../components/EnlaceBoton.jsx'
import Icono from '../components/Icono.jsx'
import IlustracionTaller from '../components/IlustracionTaller.jsx'
import ListaOrdenes from '../components/ListaOrdenes.jsx'
import ResumenTaller from '../components/ResumenTaller.jsx'
import { ROLES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'

function formatearHoy() {
  const hoy = new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })
  return hoy.charAt(0).toUpperCase() + hoy.slice(1)
}

// El inicio muestra el resumen del taller (RF-14 mínimo: conteos por estado y alertas de
// stock) y las órdenes abiertas. Para el mecánico es su vista "Mis órdenes" (SPEC §3).
export default function Dashboard() {
  const { sesion } = useSesion()
  const { usuario } = sesion
  const esMecanico = usuario.rol === ROLES.MECANICO

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      {/* Saludo con el plano del taller de fondo (decorativo). */}
      <div className="tarjeta relative overflow-hidden">
        <div className="fondo-plano-claro absolute inset-0" aria-hidden="true" />
        <IlustracionTaller
          animado={false}
          className={`pointer-events-none absolute top-1/2 hidden w-56 -translate-y-1/2 text-primario/20 md:block ${
            esMecanico ? 'right-8' : 'right-52'
          }`} />
        <div className="relative flex flex-wrap items-center justify-between gap-4 p-5 sm:px-6 sm:py-9">
          <div className="flex flex-col gap-1">
            <p className="text-sm font-medium text-texto-suave">{formatearHoy()}</p>
            <h1 className="text-2xl font-semibold sm:text-3xl">Hola, {usuario.nombre.split(' ')[0]}</h1>
          </div>
          {!esMecanico && (
            <EnlaceBoton to="/ordenes/nueva">
              <Icono nombre="mas" />
              Nueva orden
            </EnlaceBoton>
          )}
        </div>
      </div>

      {!esMecanico && <ResumenTaller />}

      <section aria-labelledby="titulo-abiertas" className="flex flex-col gap-3">
        <h2 id="titulo-abiertas" className="text-lg font-semibold">
          {esMecanico ? 'Mis órdenes abiertas' : 'Órdenes abiertas'}
        </h2>
        <ListaOrdenes
          filtros={{ abiertas: true }}
          tamano={10}
          vacio={
            esMecanico
              ? {
                  titulo: 'No tiene órdenes asignadas',
                  texto: 'Cuando le asignen un carro, aparecerá aquí para que registre el diagnóstico y el trabajo.',
                }
              : {
                  titulo: 'No hay carros en el taller',
                  texto: 'Cuando reciba un carro con «Nueva orden», aquí verá su avance.',
                }
          }
        />
      </section>
    </div>
  )
}
