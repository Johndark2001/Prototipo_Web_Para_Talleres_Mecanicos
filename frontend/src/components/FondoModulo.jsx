import { useLocation } from 'react-router'

import clientes from '../assets/fondos/clientes.svg'
import inicio from '../assets/fondos/inicio.svg'
import inventario from '../assets/fondos/inventario.svg'
import ordenes from '../assets/fondos/ordenes.svg'
import usuarios from '../assets/fondos/usuarios.svg'
import vehiculos from '../assets/fondos/vehiculos.svg'

// Escena de fondo de cada módulo: ilustraciones vectoriales de la misma familia que la del
// inicio de sesión (mismo trazo, misma tinta verde petróleo, mismo carro), así se ven
// nítidas en cualquier pantalla y ningún módulo parece de otra aplicación.
// Los detalles y formularios heredan la escena de su módulo (/ordenes/7 → órdenes).
const ESCENAS = [
  { prefijo: '/ordenes', src: ordenes },
  { prefijo: '/clientes', src: clientes },
  { prefijo: '/vehiculos', src: vehiculos },
  { prefijo: '/inventario', src: inventario },
  { prefijo: '/usuarios', src: usuarios },
]

// PRUEBA VISUAL al 50 % (pedida por el autor; el rango acordado era 10–15 %): es identidad, no contenido.
export const OPACIDAD_FONDO = 0.5

function escenaDe(ruta) {
  return ESCENAS.find(({ prefijo }) => ruta === prefijo || ruta.startsWith(`${prefijo}/`))?.src ?? inicio
}

export default function FondoModulo() {
  const { pathname } = useLocation()
  const src = escenaDe(pathname)

  return (
    // Capa fija detrás del contenido (el contenedor del Layout aísla el apilamiento). En PC
    // empieza después de la barra lateral; no recibe clics ni la leen los lectores de pantalla.
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden md:left-64">
      {/* Luz ambiental verde muy suave en la esquina de la escena, difuminada. */}
      <div className="absolute -bottom-40 -right-40 size-[40rem] rounded-full bg-primario/10 blur-3xl" />
      {/* La escena se desvanece hacia arriba y a la izquierda: los títulos y filtros
          quedan siempre sobre fondo limpio. key reinicia el fundido solo al cambiar de módulo. */}
      <img
        key={src}
        src={src}
        alt=""
        draggable="false"
        style={{ opacity: OPACIDAD_FONDO }}
        className="fondo-escena absolute bottom-14 right-0 w-full max-w-[72rem] select-none md:bottom-0"
      />
    </div>
  )
}
