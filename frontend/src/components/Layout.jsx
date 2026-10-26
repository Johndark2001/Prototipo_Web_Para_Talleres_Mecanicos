import { NavLink, Outlet } from 'react-router'

import { ETIQUETAS_ROL, ROLES, ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'
import BuscadorPlaca from './BuscadorPlaca.jsx'
import Icono from './Icono.jsx'

// Cada semana se agregan aquí los módulos nuevos (clientes, órdenes, inventario…).
const MENU = [
  { a: '/', etiqueta: 'Inicio', icono: 'inicio', roles: Object.values(ROLES) },
  { a: '/ordenes', etiqueta: 'Órdenes', icono: 'orden', roles: ROLES_EDITAN_CLIENTES },
  { a: '/ordenes', etiqueta: 'Mis órdenes', icono: 'orden', roles: [ROLES.MECANICO] },
  { a: '/clientes', etiqueta: 'Clientes', icono: 'cliente', roles: Object.values(ROLES) },
  { a: '/vehiculos', etiqueta: 'Vehículos', icono: 'carro', roles: Object.values(ROLES) },
  { a: '/inventario', etiqueta: 'Inventario', icono: 'caja', roles: Object.values(ROLES) },
  { a: '/usuarios', etiqueta: 'Usuarios', icono: 'usuarios', roles: [ROLES.ADMIN] },
]

function claseEnlace({ isActive }) {
  return `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? 'bg-primario-suave text-primario-oscuro' : 'text-texto-suave hover:bg-fondo'
  }`
}

function claseEnlaceMovil({ isActive }) {
  return `flex min-h-14 flex-1 flex-col items-center justify-center gap-0.5 text-xs font-medium ${
    isActive ? 'text-primario' : 'text-texto-suave'
  }`
}

export default function Layout() {
  const { sesion, cerrarSesion } = useSesion()
  const { usuario, taller } = sesion
  const opciones = MENU.filter((item) => item.roles.includes(usuario.rol))

  return (
    <div className="flex min-h-dvh flex-col md:flex-row">
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-superficie focus:p-2"
      >
        Saltar al contenido
      </a>

      {/* Navegación lateral (PC) */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-borde bg-superficie md:flex">
        <div className="flex items-center gap-2 border-b border-borde px-4 py-4">
          <Icono nombre="llave" className="size-6 text-primario" />
          <span className="font-semibold">Taller Digital</span>
        </div>
        <nav aria-label="Principal" className="flex flex-1 flex-col gap-1 p-3">
          {opciones.map((item) => (
            <NavLink key={item.a} to={item.a} end={item.a === '/'} className={claseEnlace}>
              <Icono nombre={item.icono} />
              {item.etiqueta}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-borde bg-superficie px-4 py-3">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold">{taller.nombre}</p>
            <p className="truncate text-xs text-texto-suave">
              {usuario.nombre} · {ETIQUETAS_ROL[usuario.rol]}
            </p>
          </div>
          {/* En el celular el buscador ocupa su propia fila, debajo del nombre del taller. */}
          <BuscadorPlaca className="order-last w-full md:order-none md:w-72" />
          <button
            type="button"
            onClick={cerrarSesion}
            className="inline-flex min-h-11 items-center gap-2 rounded-md px-3 text-sm font-medium text-texto-suave hover:bg-fondo"
          >
            <Icono nombre="salir" />
            <span>Salir</span>
          </button>
        </header>

        <main id="contenido" className="flex-1 px-4 py-6 pb-24 md:px-8 md:pb-8">
          <Outlet />
        </main>
      </div>

      {/* Navegación inferior (celular), al alcance del pulgar */}
      {opciones.length > 1 && (
        <nav
          aria-label="Principal"
          className="fixed inset-x-0 bottom-0 flex border-t border-borde bg-superficie md:hidden"
        >
          {opciones.map((item) => (
            <NavLink key={item.a} to={item.a} end={item.a === '/'} className={claseEnlaceMovil}>
              <Icono nombre={item.icono} />
              {item.etiqueta}
            </NavLink>
          ))}
        </nav>
      )}
    </div>
  )
}
