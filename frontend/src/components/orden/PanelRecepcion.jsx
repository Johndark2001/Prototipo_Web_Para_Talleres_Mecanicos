import { useState } from 'react'

import { api, erroresPorCampo } from '../../api/cliente.js'
import { formatearDia, formatearFechaHora, formatearKilometraje } from '../../formato.js'
import Boton from '../Boton.jsx'
import CampoFormulario from '../CampoFormulario.jsx'

function Dato({ etiqueta, children }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-texto-suave">{etiqueta}</dt>
      <dd className="mt-0.5 whitespace-pre-line break-words">{children || '—'}</dd>
    </div>
  )
}

/** Datos con los que se recibió el carro; ADMIN y RECEPCION pueden corregirlos. */
export default function PanelRecepcion({ orden, alActualizar }) {
  const [editando, setEditando] = useState(false)
  const [datos, setDatos] = useState(null)
  const [errores, setErrores] = useState({})
  const [guardando, setGuardando] = useState(false)

  function abrir() {
    setDatos({
      motivo_ingreso: orden.motivo_ingreso,
      kilometraje: orden.kilometraje ?? '',
      fecha_entrega_estimada: orden.fecha_entrega_estimada ?? '',
    })
    setErrores({})
    setEditando(true)
  }

  async function guardar(evento) {
    evento.preventDefault()
    // Solo se envía lo que cambió: una fecha estimada ya vencida no debe bloquear otros cambios.
    const cambios = Object.fromEntries(
      Object.entries(datos).filter(([campo, valor]) => valor !== (orden[campo] ?? '')),
    )
    if (Object.keys(cambios).length === 0) {
      setEditando(false)
      return
    }
    setGuardando(true)
    try {
      const actualizada = await api.patch(`/ordenes/${orden.id}`, cambios)
      setEditando(false)
      alActualizar(actualizada, 'Datos de recepción actualizados')
    } catch (err) {
      setErrores({ ...erroresPorCampo(err), general: err.message })
    }
    setGuardando(false)
  }

  if (editando) {
    const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })
    return (
      <form onSubmit={guardar} noValidate className="flex flex-col gap-3 tarjeta p-4">
        {errores.general && !Object.keys(errores).some((c) => c !== 'general') && (
          <p className="text-sm text-peligro">{errores.general}</p>
        )}
        <CampoFormulario etiqueta="Motivo de ingreso" value={datos.motivo_ingreso} onChange={cambiar('motivo_ingreso')} error={errores.motivo_ingreso} obligatorio />
        <div className="grid gap-3 sm:grid-cols-2">
          <CampoFormulario etiqueta="Kilometraje" type="number" inputMode="numeric" min={0} value={datos.kilometraje} onChange={cambiar('kilometraje')} error={errores.kilometraje} />
          <CampoFormulario etiqueta="Entrega estimada" type="date" value={datos.fecha_entrega_estimada} onChange={cambiar('fecha_entrega_estimada')} error={errores.fecha_entrega_estimada} />
        </div>
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Boton variante="secundario" onClick={() => setEditando(false)} disabled={guardando}>
            Cancelar
          </Boton>
          <Boton type="submit" cargando={guardando}>
            Guardar
          </Boton>
        </div>
      </form>
    )
  }

  return (
    <section aria-label="Datos de recepción" className="flex flex-col gap-3 tarjeta p-4">
      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <Dato etiqueta="Motivo de ingreso">{orden.motivo_ingreso}</Dato>
        </div>
        <Dato etiqueta="Kilometraje">{orden.kilometraje != null && formatearKilometraje(orden.kilometraje)}</Dato>
        <Dato etiqueta="Recibido">
          {formatearFechaHora(orden.fecha_ingreso)} por {orden.creador.nombre}
        </Dato>
        <Dato etiqueta="Entrega estimada">
          {orden.fecha_entrega_estimada && formatearDia(orden.fecha_entrega_estimada)}
        </Dato>
        {orden.fecha_entrega && <Dato etiqueta="Entregado">{formatearFechaHora(orden.fecha_entrega)}</Dato>}
        {orden.motivo_cancelacion && <Dato etiqueta="Motivo de cancelación">{orden.motivo_cancelacion}</Dato>}
      </dl>
      {orden.puede_editar_recepcion && (
        <Boton variante="texto" onClick={abrir} className="self-start">
          Corregir datos de recepción
        </Boton>
      )}
    </section>
  )
}
