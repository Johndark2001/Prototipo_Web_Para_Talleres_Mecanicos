import { NavLink, Outlet } from 'react-router'

import { ETIQUETAS_ROL, ROLES, ROLES_EDITAN_CLIENTES } from '../constantes.js'
import { useSesion } from '../sesion/contexto.js'
import BuscadorPlaca from './BuscadorPlaca.jsx'
import Icono from './Icono.jsx'
import Logo, { MarcaLogo } from './Logo.jsx'

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

// Navegación de todos los días: solo color y fondo cambian, en 150 ms (sin desplazamientos).
function claseEnlace({ isActive }) {
  return `group flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm transition-colors duration-150 ease-salida ${
    isActive
      ? 'bg-white/10 font-semibold text-white'
      : 'font-medium text-lateral-texto hover:bg-white/5 hover:text-white'
  }`
}

function claseIconoLateral(isActive) {
  return `size-5 shrink-0 transition-colors duration-150 ${
    isActive ? 'text-lateral-activo' : 'text-lateral-texto/70 group-hover:text-white'
  }`
}

function claseEnlaceMovil({ isActive }) {
  return `group flex min-h-14 flex-1 flex-col items-center justify-center gap-1 text-xs transition-colors duration-150 ${
    isActive ? 'font-semibold text-primario-oscuro' : 'font-medium text-texto-suave'
  }`
}

function iniciales(nombre) {
  return nombre
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0].toUpperCase())
    .join('')
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
      <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col bg-lateral md:flex">
        <div className="flex h-16 items-center border-b border-lateral-borde px-5">
          <Logo tono="claro" />
        </div>
        <nav aria-label="Principal" className="flex flex-1 flex-col gap-1 p-3">
          {opciones.map((item) => (
            <NavLink key={item.a} to={item.a} end={item.a === '/'} className={claseEnlace}>
              {({ isActive }) => (
                <>
                  <Icono nombre={item.icono} className={claseIconoLateral(isActive)} />
                  {item.etiqueta}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="z-30 flex flex-wrap items-center justify-between gap-3 border-b border-borde bg-superficie/90 px-4 py-3 backdrop-blur md:h-16 md:sticky md:top-0 md:flex-nowrap md:px-8 md:py-0">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <MarcaLogo className="size-8 shrink-0 md:hidden" />
            <span
              aria-hidden="true"
              className="hidden size-9 shrink-0 items-center justify-center rounded-full bg-primario-suave text-sm font-semibold text-primario-oscuro sm:flex"
            >
              {iniciales(usuario.nombre)}
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{taller.nombre}</p>
              <p className="truncate text-xs text-texto-suave">
                {usuario.nombre} · {ETIQUETAS_ROL[usuario.rol]}
              </p>
            </div>
          </div>
          {/* En el celular el buscador ocupa su propia fila, debajo del nombre del taller. */}
          <BuscadorPlaca className="order-last w-full md:order-none md:w-72" />
          <button
            type="button"
            onClick={cerrarSesion}
            className="inline-flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm font-medium text-texto-suave transition-colors duration-150 hover:bg-fondo hover:text-texto active:scale-[0.97]"
          >
            <Icono nombre="salir" />
            <span>Salir</span>
          </button>
        </header>

        <main id="contenido" className="flex-1 px-4 py-6 pb-24 md:px-8 md:pb-10">
          <Outlet />
        </main>
      </div>

      {/* Navegación inferior (celular), al alcance del pulgar */}
      {opciones.length > 1 && (
        <nav
          aria-label="Principal"
          className="fixed inset-x-0 bottom-0 z-30 flex border-t border-borde bg-superficie/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:hidden"
        >
          {opciones.map((item) => (
            <NavLink key={item.a} to={item.a} end={item.a === '/'} className={claseEnlaceMovil}>
              {({ isActive }) => (
                <>
                  <span
                    className={`flex h-7 w-12 items-center justify-center rounded-full transition-colors duration-150 ${
                      isActive ? 'bg-primario-suave text-primario' : 'group-hover:bg-fondo'
                    }`}
                  >
                    <Icono nombre={item.icono} />
                  </span>
                  {item.etiqueta}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      )}
    </div>
  )
}
