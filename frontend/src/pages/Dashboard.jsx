import EnlaceBoton from '../components/EnlaceBoton.jsx'
import Icono from '../components/Icono.jsx'
import ListaOrdenes from '../components/ListaOrdenes.jsx'
import { ROLES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'

// Semana 3: el inicio muestra las órdenes abiertas; para el mecánico es su vista
// "Mis órdenes" (SPEC §3). En la semana 4 se agregan los conteos por estado y las
// alertas de stock (RF-14 mínimo).
export default function Dashboard() {
  const { sesion } = useSesion()
  const { usuario, taller } = sesion
  const esMecanico = usuario.rol === ROLES.MECANICO

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Hola, {usuario.nombre.split(' ')[0]}</h1>
          <p className="text-sm text-texto-suave">{taller.nombre}</p>
        </div>
        {!esMecanico && (
          <EnlaceBoton to="/ordenes/nueva">
            <Icono nombre="mas" />
            Nueva orden
          </EnlaceBoton>
        )}
      </div>

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
