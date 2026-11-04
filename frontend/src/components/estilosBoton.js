// Estilo único de botones y enlaces con forma de botón (SPEC §11: BotonPrimario y variantes).
// Las transiciones nombran sus propiedades y duran 150 ms; al presionar, el botón se hunde
// un poco para confirmar que el taller tocó (retroalimentación inmediata).
const BASE =
  'inline-flex min-h-11 select-none items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold ' +
  'transition-[background-color,border-color,color,box-shadow,transform] duration-150 ease-salida ' +
  'active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-60 disabled:active:scale-100'

const VARIANTES = {
  primario: 'bg-primario text-white shadow-boton hover:bg-primario-oscuro',
  secundario: 'border border-borde bg-superficie text-texto shadow-tarjeta hover:border-texto-suave/40 hover:bg-fondo',
  peligro: 'bg-peligro text-white shadow-boton hover:bg-peligro/90',
  texto: 'text-primario hover:bg-primario-suave',
}

export function claseBoton(variante = 'primario', extra = '') {
  return `${BASE} ${VARIANTES[variante]} ${extra}`
}
