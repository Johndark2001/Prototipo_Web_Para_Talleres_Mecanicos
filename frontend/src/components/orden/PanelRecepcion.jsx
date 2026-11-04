import { useState } from 'react'

import { api, erroresPorCampo } from '../../api/cliente.js'
import { formatearDia, formatearFechaHora, formatearKilometraje } from '../../formato.js'
import { OTRO, nombreProblema } from '../../problema.js'
import Boton from '../Boton.jsx'
import CampoFormulario from '../CampoFormulario.jsx'
import CamposProblema from './CamposProblema.jsx'

function Dato({ etiqueta, children, ancho = false }) {
  return (
    <div className={ancho ? 'sm:col-span-2' : undefined}>
      <dt className="text-xs font-medium uppercase tracking-wide text-texto-suave">{etiqueta}</dt>
      <dd className="mt-0.5 whitespace-pre-line break-words">{children || '—'}</dd>
    </div>
  )
}

const valorDe = (orden) => ({
  categoria_problema: orden.categoria_problema ?? '',
  categoria_otro: orden.categoria_otro ?? '',
  observacion_cliente: orden.observacion_cliente ?? '',
  kilometraje: orden.kilometraje ?? '',
  fecha_entrega_estimada: orden.fecha_entrega_estimada ?? '',
})

/**
 * Información general con que se recibió el vehículo. ADMIN y RECEPCION pueden corregirla,
 * incluida la categoría del problema (cambio #5); el mecánico solo la consulta.
 */
export default function PanelRecepcion({ orden, alActualizar }) {
  const [editando, setEditando] = useState(false)
  const [datos, setDatos] = useState(null)
  const [errores, setErrores] = useState({})
  const [guardando, setGuardando] = useState(false)

  function abrir() {
    setDatos(valorDe(orden))
    setErrores({})
    setEditando(true)
  }

  async function guardar(evento) {
    evento.preventDefault()
    if (orden.categoria_problema && !datos.categoria_problema) {
      setErrores({ categoria_problema: 'Elija la categoría del problema' })
      return
    }
    // Solo se envía lo que cambió: una fecha estimada ya vencida no debe bloquear otros cambios.
    const original = valorDe(orden)
    const cambios = Object.fromEntries(Object.entries(datos).filter(([campo, valor]) => valor !== original[campo]))
    // Una orden anterior al catálogo puede quedar sin categoría; no se envía vacía.
    if (cambios.categoria_problema === '') delete cambios.categoria_problema
    if ('categoria_otro' in cambios && datos.categoria_problema !== OTRO) delete cambios.categoria_otro
    if (datos.categoria_problema === OTRO && 'categoria_problema' in cambios) {
      cambios.categoria_otro = datos.categoria_otro
    }
    if (Object.keys(cambios).length === 0) {
      setEditando(false)
      return
    }
    setGuardando(true)
    try {
      const actualizada = await api.patch(`/ordenes/${orden.id}`, cambios)
      setEditando(false)
      alActualizar(actualizada, 'Información de la orden actualizada')
    } catch (err) {
      setErrores({ ...erroresPorCampo(err), general: err.message })
    }
    setGuardando(false)
  }

  if (editando) {
    const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })
    return (
      <form onSubmit={guardar} noValidate className="flex flex-col gap-4 tarjeta p-4">
        {errores.general && !Object.keys(errores).some((c) => c !== 'general') && (
          <p className="text-sm text-peligro">{errores.general}</p>
        )}
        <CamposProblema
          tipo={orden.vehiculo.tipo}
          datos={datos}
          alCambiar={(campo, valor) => setDatos({ ...datos, [campo]: valor })}
          errores={errores}
        />
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

  const problema = nombreProblema(orden)
  return (
    <section aria-label="Datos de recepción" className="flex flex-col gap-3 tarjeta p-4">
      <dl className="grid gap-3 sm:grid-cols-2">
        <Dato etiqueta="Categoría del problema" ancho>
          {problema ?? <span className="text-texto-suave">Sin categoría (orden registrada antes del catálogo)</span>}
        </Dato>
        <Dato etiqueta="Observación reportada por el cliente" ancho>
          {orden.observacion_cliente ?? orden.motivo_ingreso}
        </Dato>
        <Dato etiqueta="Kilometraje">{orden.kilometraje != null && formatearKilometraje(orden.kilometraje)}</Dato>
        <Dato etiqueta="Recibido">
          {formatearFechaHora(orden.fecha_ingreso)} por {orden.creador.nombre}
        </Dato>
        <Dato etiqueta="Entrega estimada">
          {orden.fecha_entrega_estimada && formatearDia(orden.fecha_entrega_estimada)}
        </Dato>
        {orden.fecha_entrega && <Dato etiqueta="Entregado">{formatearFechaHora(orden.fecha_entrega)}</Dato>}
        {orden.motivo_cancelacion && <Dato etiqueta="Motivo de cancelación" ancho>{orden.motivo_cancelacion}</Dato>}
      </dl>
      {orden.puede_editar_recepcion && (
        <Boton variante="texto" onClick={abrir} className="self-start">
          Corregir datos de recepción
        </Boton>
      )}
    </section>
  )
}
