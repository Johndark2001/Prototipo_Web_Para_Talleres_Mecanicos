import { useConsulta } from '../../hooks/useConsulta.js'
import CampoFormulario from '../CampoFormulario.jsx'

/** Lista de mecánicos activos con su carga actual, para repartir el trabajo (RF-07). */
export default function SelectorMecanico({ valor, alCambiar, error, etiqueta = 'Mecánico', excluir }) {
  const { datos: mecanicos, error: errorCarga } = useConsulta('/mecanicos')
  const opciones = (mecanicos ?? []).filter((m) => m.id !== excluir)

  return (
    <CampoFormulario
      etiqueta={etiqueta}
      error={error ?? errorCarga?.message}
      ayuda={mecanicos && opciones.length === 0 ? 'No hay otros mecánicos activos.' : undefined}
    >
      {(propsCampo) => (
        <select
          {...propsCampo}
          value={valor ?? ''}
          onChange={(e) => alCambiar(e.target.value ? Number(e.target.value) : null)}
          disabled={!mecanicos}
        >
          <option value="">{mecanicos ? 'Sin asignar por ahora' : 'Cargando…'}</option>
          {opciones.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre} ({m.ordenes_abiertas} {m.ordenes_abiertas === 1 ? 'orden abierta' : 'abiertas'})
            </option>
          ))}
        </select>
      )}
    </CampoFormulario>
  )
}
