import { useState } from 'react'

import { api, erroresPorCampo } from '../../api/cliente.js'
import Boton from '../Boton.jsx'
import CampoFormulario from '../CampoFormulario.jsx'
import Icono from '../Icono.jsx'
import SelectorMecanico from './SelectorMecanico.jsx'

/** Mecánico asignado y, para ADMIN y RECEPCION, la asignación o reasignación (RN-14). */
export default function PanelMecanico({ orden, alActualizar, alError }) {
  const [editando, setEditando] = useState(false)
  const [mecanicoId, setMecanicoId] = useState(null)
  const [nota, setNota] = useState('')
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const reasignar = Boolean(orden.mecanico)

  async function guardar(evento) {
    evento.preventDefault()
    if (!mecanicoId) {
      setError('Elija un mecánico')
      return
    }
    setGuardando(true)
    try {
      const actualizada = await api.post(`/ordenes/${orden.id}/asignaciones`, {
        mecanico_id: mecanicoId,
        nota,
      })
      setEditando(false)
      alActualizar(actualizada, `Orden asignada a ${actualizada.mecanico.nombre}`)
    } catch (err) {
      const errores = erroresPorCampo(err)
      if (errores.mecanico_id) setError(errores.mecanico_id)
      else alError(err.message)
    }
    setGuardando(false)
  }

  return (
    <section aria-labelledby="titulo-mecanico" className="flex flex-col gap-3 tarjeta p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 id="titulo-mecanico" className="text-xs font-medium uppercase tracking-wide text-texto-suave">
            Mecánico
          </h2>
          <p className="flex items-center gap-2 font-medium">
            <Icono nombre="llave" className="size-4 text-texto-suave" />
            {orden.mecanico ? orden.mecanico.nombre : 'Sin asignar'}
          </p>
        </div>
        {orden.puede_asignar && !editando && (
          <Boton variante="secundario" onClick={() => setEditando(true)}>
            {reasignar ? 'Reasignar' : 'Asignar'}
          </Boton>
        )}
      </div>

      {editando && (
        <form onSubmit={guardar} noValidate className="flex flex-col gap-3 border-t border-borde pt-3">
          <SelectorMecanico
            etiqueta={reasignar ? 'Nuevo mecánico' : 'Mecánico'}
            valor={mecanicoId}
            alCambiar={(id) => {
              setMecanicoId(id)
              setError(null)
            }}
            excluir={orden.mecanico?.id}
            error={error}
          />
          {reasignar && (
            <CampoFormulario
              etiqueta="Motivo de la reasignación (opcional)"
              value={nota}
              onChange={(e) => setNota(e.target.value)}
              maxLength={1000}
            />
          )}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Boton variante="secundario" onClick={() => setEditando(false)} disabled={guardando}>
              Cancelar
            </Boton>
            <Boton type="submit" cargando={guardando}>
              Guardar
            </Boton>
          </div>
        </form>
      )}
    </section>
  )
}
