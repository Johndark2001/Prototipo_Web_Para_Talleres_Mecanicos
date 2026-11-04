import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'

import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import Icono from '../components/Icono.jsx'
import IlustracionTaller from '../components/IlustracionTaller.jsx'
import Logo from '../components/Logo.jsx'
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
    <main className="grid min-h-dvh bg-superficie lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
      {/* Panel de marca: plano técnico del taller con la ilustración (decorativo). */}
      <section
        aria-hidden="true"
        className="fondo-plano relative hidden overflow-hidden bg-lateral text-lateral-activo lg:flex lg:flex-col lg:justify-between lg:p-12"
      >
        <div className="pointer-events-none absolute -right-24 -top-24 size-96 rounded-full bg-primario/30 blur-3xl" />
        <Logo tono="claro" tamano="size-10" className="relative" />
        <IlustracionTaller className="relative mx-auto w-full max-w-xl" />
        <div className="relative flex max-w-md flex-col gap-3">
          <p className="text-3xl font-semibold leading-tight tracking-tight text-white">
            Del ingreso a la entrega, cada carro y cada moto en orden.
          </p>
          <p className="text-base text-lateral-texto">
            Órdenes, diagnóstico, repuestos y liquidación del taller en un solo lugar.
          </p>
        </div>
      </section>

      <div className="fondo-plano-claro flex items-center justify-center px-4 py-10 lg:bg-none">
        <div className="w-full max-w-sm animate-aparecer">
          <div className="mb-8 flex flex-col items-center gap-4 text-center lg:items-start lg:text-left">
            <Logo tamano="size-11" className="lg:hidden" />
            <IlustracionTaller className="w-52 text-primario/70 lg:hidden" />
            <div className="flex flex-col gap-1">
              <h1 className="text-2xl font-semibold">Ingresar al taller</h1>
              <p className="text-sm text-texto-suave">Use el correo y la clave que le dio su taller.</p>
            </div>
          </div>

          <form
            onSubmit={enviar}
            noValidate
            className="tarjeta flex flex-col gap-4 p-6 lg:border-0 lg:p-0 lg:shadow-none"
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
                    className="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-lg text-texto-suave transition-colors duration-150 hover:text-texto"
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
      </div>
    </main>
  )
}
