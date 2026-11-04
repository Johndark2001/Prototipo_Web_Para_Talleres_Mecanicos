import EnlaceBoton from '../components/EnlaceBoton.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'

export default function NoEncontrada() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-md items-center px-4">
      <EstadoVacio
        icono="alerta"
        titulo="Esta página no existe"
        texto="Revise la dirección o vuelva al inicio."
      >
        <EnlaceBoton to="/">Ir al inicio</EnlaceBoton>
      </EstadoVacio>
    </main>
  )
}
