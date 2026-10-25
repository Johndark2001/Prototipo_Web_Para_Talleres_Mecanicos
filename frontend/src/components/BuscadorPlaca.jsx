import { useState } from 'react'
import { useNavigate } from 'react-router'

import { api, conParametros } from '../api/cliente.js'
import { normalizarPlaca } from '../formato.js'
import Icono from './Icono.jsx'

/**
 * Búsqueda global por placa de la barra superior (SPEC §11). Si la placa existe tal cual,
 * abre el carro directamente; si no, muestra las coincidencias parciales.
 */
export default function BuscadorPlaca({ className = '' }) {
  const navegar = useNavigate()
  const [texto, setTexto] = useState('')
  const [buscando, setBuscando] = useState(false)

  async function buscar(evento) {
    evento.preventDefault()
    const placa = normalizarPlaca(texto)
    if (!placa) return
    setBuscando(true)
    let destino = conParametros('/vehiculos', { placa })
    try {
      const { data } = await api.get(conParametros('/vehiculos', { placa, page_size: 1 }))
      if (data[0]?.placa === placa) destino = `/vehiculos/${data[0].id}`
    } catch {
      // Si la consulta falla, la pantalla de vehículos mostrará el error con su botón de reintento.
    }
    setBuscando(false)
    setTexto('')
    navegar(destino)
  }

  return (
    <form role="search" onSubmit={buscar} className={`flex ${className}`}>
      <label htmlFor="buscar-placa" className="sr-only">
        Buscar placa
      </label>
      <input
        id="buscar-placa"
        type="search"
        value={texto}
        onChange={(e) => setTexto(e.target.value.toUpperCase())}
        placeholder="Buscar placa"
        autoComplete="off"
        autoCapitalize="characters"
        maxLength={12}
        className="min-h-11 w-full min-w-0 rounded-l-md border border-r-0 border-borde bg-superficie px-3 font-mono text-base uppercase placeholder:font-sans placeholder:normal-case sm:text-sm"
      />
      <button
        type="submit"
        disabled={buscando}
        aria-label="Buscar"
        className="inline-flex min-h-11 items-center rounded-r-md bg-primario px-3 text-white hover:bg-primario-oscuro disabled:opacity-60"
      >
        <Icono nombre="buscar" />
      </button>
    </form>
  )
}
