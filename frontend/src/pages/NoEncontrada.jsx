import { Link } from 'react-router'

import EstadoVacio from '../components/EstadoVacio.jsx'

export default function NoEncontrada() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-md items-center px-4">
      <EstadoVacio
        icono="alerta"
        titulo="Esta página no existe"
        texto="Revise la dirección o vuelva al inicio."
      >
        <Link to="/" className="font-semibold text-primario underline">
          Ir al inicio
        </Link>
      </EstadoVacio>
    </main>
  )
}
