import EstadoVacio from '../components/EstadoVacio.jsx'
import { ROLES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'

// Semana 1: el dashboard existe pero aún no hay órdenes. En la semana 4 muestra
// los conteos por estado y las alertas de stock (RF-14 mínimo).
const MENSAJES = {
  [ROLES.ADMIN]: {
    titulo: 'Todavía no hay órdenes registradas',
    texto: 'Cuando el taller reciba vehículos, aquí verá el resumen del día y las alertas de inventario.',
  },
  [ROLES.RECEPCION]: {
    titulo: 'Todavía no hay órdenes registradas',
    texto: 'Cuando reciba el primer vehículo, aquí verá las órdenes del día.',
  },
  [ROLES.MECANICO]: {
    titulo: 'No tiene órdenes asignadas',
    texto: 'Cuando le asignen un vehículo, aparecerá aquí para que registre el diagnóstico y el trabajo.',
  },
}

export default function Dashboard() {
  const { sesion } = useSesion()
  const { usuario, taller } = sesion
  const mensaje = MENSAJES[usuario.rol]

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Hola, {usuario.nombre.split(' ')[0]}</h1>
        <p className="text-sm text-texto-suave">{taller.nombre}</p>
      </div>
      <EstadoVacio icono="inicio" titulo={mensaje.titulo} texto={mensaje.texto} />
    </div>
  )
}
