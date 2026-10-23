import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'

import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import Icono from '../components/Icono.jsx'
import { useSesion } from '../sesion/contexto.js'

export default function Login() {
  const { sesion, iniciarSesion } = useSesion()
  const navegar = useNavigate()
  const ubicacion = useLocation()
  const [email, setEmail] = useState('')
  const [clave, setClave] = useState('')
  const [verClave, setVerClave] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  const destino = ubicacion.state?.desde ?? '/'
  if (sesion) return <Navigate to={destino} replace />

  async function enviar(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await iniciarSesion(email, clave)
      navegar(destino, { replace: true })
    } catch (err) {
      setError(err.message)
      setEnviando(false)
    }
  }

  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <span className="rounded-full bg-primario-suave p-3 text-primario">
            <Icono nombre="llave" className="size-7" />
          </span>
          <h1 className="text-2xl font-semibold">Taller Digital</h1>
          <p className="text-sm text-texto-suave">Ingrese con el correo que le dio su taller</p>
        </div>

        <form
          onSubmit={enviar}
          noValidate
          className="flex flex-col gap-4 rounded-lg border border-borde bg-superficie p-5 shadow-sm"
        >
          {error && <Aviso tipo="error">{error}</Aviso>}

          <CampoFormulario
            etiqueta="Correo"
            type="email"
            autoComplete="username"
            inputMode="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            obligatorio
            autoFocus
          />

          <CampoFormulario etiqueta="Clave" obligatorio>
            {(propsCampo) => (
              <div className="relative">
                <input
                  {...propsCampo}
                  type={verClave ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={clave}
                  onChange={(e) => setClave(e.target.value)}
                  required
                  className={`${propsCampo.className} pr-12`}
                />
                <button
                  type="button"
                  onClick={() => setVerClave((v) => !v)}
                  className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-texto-suave"
                  aria-label={verClave ? 'Ocultar clave' : 'Mostrar clave'}
                  aria-pressed={verClave}
                >
                  <Icono nombre={verClave ? 'ojoTachado' : 'ojo'} />
                </button>
              </div>
            )}
          </CampoFormulario>

          <Boton type="submit" cargando={enviando} disabled={!email || !clave} className="w-full">
            Ingresar
          </Boton>
        </form>
      </div>
    </main>
  )
}
