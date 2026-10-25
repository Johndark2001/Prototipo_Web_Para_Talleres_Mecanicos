import { useState } from 'react'

import { erroresPorCampo } from '../../api/cliente.js'
import { ACCIONES_ESTADO, ESTADOS_ORDEN } from '../../constantes.js'
import Boton from '../Boton.jsx'
import DialogoConfirmacion from '../DialogoConfirmacion.jsx'
import DialogoNota from '../DialogoNota.jsx'
import Icono from '../Icono.jsx'

function textoBoton(transicion) {
  if (transicion.tipo === 'RETROCESO') return `Devolver a ${ESTADOS_ORDEN[transicion.estado].etiqueta}`
  return ACCIONES_ESTADO[transicion.estado]
}

function varianteBoton(transicion, principal) {
  if (transicion.tipo === 'CANCELACION') return 'texto'
  return transicion === principal ? 'primario' : 'secundario'
}

// Qué pide cada cambio antes de aplicarse (prevención de errores, SPEC §11).
function confirmacionDe(t, orden) {
  if (t.tipo === 'CANCELACION') {
    return {
      nota: true,
      titulo: `¿Cancelar la orden #${orden.numero}?`,
      mensaje: 'La orden queda cerrada y no se podrá modificar.',
      etiqueta: 'Motivo de la cancelación',
      textoConfirmar: 'Cancelar orden',
      variante: 'peligro',
    }
  }
  if (t.tipo === 'RETROCESO') {
    return {
      nota: true,
      titulo: `¿Devolver la orden a «${ESTADOS_ORDEN[t.estado].etiqueta}»?`,
      etiqueta: 'Por qué la devuelve',
      textoConfirmar: 'Devolver',
    }
  }
  if (t.estado === 'ESPERANDO_REPUESTOS') {
    return {
      nota: true,
      opcional: true,
      titulo: 'La orden queda esperando repuestos',
      etiqueta: 'Qué repuesto falta',
      textoConfirmar: 'Confirmar',
    }
  }
  if (t.tipo === 'ENTREGA') {
    return {
      titulo: `¿Entregar el carro ${orden.vehiculo.placa}?`,
      mensaje: 'La orden se cierra como entregada y ya no se podrá modificar.',
      textoConfirmar: 'Entregar',
    }
  }
  return null
}

/** Botones con los cambios de estado que el backend permite a este usuario (§7). */
export default function AccionesEstado({ orden, alCambiarEstado }) {
  const [pendiente, setPendiente] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [errorNota, setErrorNota] = useState(null)

  if (orden.transiciones.length === 0) return null
  const avances = orden.transiciones.filter((t) => t.tipo === 'AVANCE' || t.tipo === 'ENTREGA')
  const principal = avances[avances.length - 1]
  // Avisos de RN-13 y RN-17 antes de que el usuario lo intente.
  const avisos = []
  if (avances.some((t) => t.estado === 'EN_DIAGNOSTICO') && !orden.mecanico) {
    avisos.push('Asigne un mecánico para iniciar el diagnóstico.')
  }

  async function ejecutar(transicion, nota) {
    setEnviando(true)
    setErrorNota(null)
    const error = await alCambiarEstado(transicion, nota)
    setEnviando(false)
    const errorDeNota = error && erroresPorCampo(error).nota
    if (errorDeNota) {
      setErrorNota(errorDeNota)
      return
    }
    setPendiente(null)
  }

  function pulsar(transicion) {
    if (confirmacionDe(transicion, orden)) {
      setErrorNota(null)
      setPendiente(transicion)
    } else {
      ejecutar(transicion, null)
    }
  }

  const confirmacion = pendiente && confirmacionDe(pendiente, orden)

  return (
    <section aria-label="Cambiar estado" className="flex flex-col gap-2">
      {avisos.map((aviso) => (
        <p key={aviso} className="flex items-center gap-2 text-sm text-aviso">
          <Icono nombre="alerta" className="size-4 shrink-0" />
          {aviso}
        </p>
      ))}
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
        {orden.transiciones.map((t) => (
          <Boton
            key={`${t.tipo}-${t.estado}`}
            variante={varianteBoton(t, principal)}
            onClick={() => pulsar(t)}
            disabled={enviando}
            className={t.tipo === 'CANCELACION' ? 'text-peligro sm:mr-auto' : ''}
          >
            {textoBoton(t)}
            {t === principal && <Icono nombre="derecha" className="size-4" />}
          </Boton>
        ))}
      </div>

      <DialogoNota
        abierto={Boolean(confirmacion?.nota)}
        titulo={confirmacion?.titulo}
        mensaje={confirmacion?.mensaje}
        etiqueta={confirmacion?.etiqueta}
        obligatoria={!confirmacion?.opcional}
        textoConfirmar={confirmacion?.textoConfirmar}
        variante={confirmacion?.variante}
        cargando={enviando}
        error={errorNota}
        alConfirmar={(nota) => ejecutar(pendiente, nota)}
        alCancelar={() => setPendiente(null)}
      />
      <DialogoConfirmacion
        abierto={Boolean(confirmacion && !confirmacion.nota)}
        titulo={confirmacion?.titulo}
        mensaje={confirmacion?.mensaje}
        textoConfirmar={confirmacion?.textoConfirmar}
        cargando={enviando}
        alConfirmar={() => ejecutar(pendiente, null)}
        alCancelar={() => setPendiente(null)}
      />
    </section>
  )
}
