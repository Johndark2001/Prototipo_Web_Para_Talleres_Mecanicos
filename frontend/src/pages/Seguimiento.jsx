import { useParams } from 'react-router'

import Boton from '../components/Boton.jsx'
import ChipEstado from '../components/ChipEstado.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import { MarcaLogo } from '../components/Logo.jsx'
import Placa from '../components/Placa.jsx'
import LineaTiempo from '../components/orden/LineaTiempo.jsx'
import { claseBoton } from '../components/estilosBoton.js'
import { formatearCantidad, formatearFechaHora, formatearPesos } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'

const MENSAJES = {
  RECIBIDO: 'Recibimos su carro y pronto empezamos a revisarlo.',
  EN_DIAGNOSTICO: 'Estamos revisando su carro.',
  ESPERANDO_REPUESTOS: 'Estamos esperando un repuesto para continuar.',
  REPARADO: '¡Su carro está listo! Puede pasar a recogerlo.',
  ENTREGADO: 'Su carro ya fue entregado. Gracias por su confianza.',
  CANCELADA: 'Esta orden fue cancelada.',
}

function Lineas({ titulo, lineas }) {
  if (lineas.length === 0) return null
  return (
    <div className="flex flex-col gap-1">
      <h3 className="text-sm font-semibold">{titulo}</h3>
      <ul className="divide-y divide-borde text-sm">
        {lineas.map((linea, indice) => (
          <li key={indice} className="flex justify-between gap-3 py-2">
            <span>
              {linea.nombre}
              <span className="block text-texto-suave">
                {formatearCantidad(linea.cantidad)} {linea.unidad} × {formatearPesos(linea.precio_unitario)}
              </span>
            </span>
            <span className="shrink-0 font-medium">{formatearPesos(linea.subtotal)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

/** Página pública del cliente (RF-13): sin sesión y sin datos personales (ADR-005). */
export default function Seguimiento() {
  const { codigo } = useParams()
  const { datos: orden, error, recargar } = useConsulta(`/seguimiento/${codigo}`)

  let contenido
  if (error) {
    contenido =
      error.status === 404 ? (
        <EstadoVacio
          icono="alerta"
          titulo="No encontramos esta orden"
          texto="Revise que el enlace esté completo o pídale uno nuevo al taller."
        />
      ) : (
        <EstadoVacio icono="alerta" titulo="No pudimos cargar su orden" texto={error.message}>
          <Boton onClick={recargar}>Intentar de nuevo</Boton>
        </EstadoVacio>
      )
  } else if (!orden) {
    contenido = <Esqueleto etiqueta="Cargando su orden" />
  } else {
    const etapas = orden.etapas.map((e) => ({ estado_nuevo: e.estado, fecha: e.fecha }))
    const ultima = etapas[etapas.length - 1]
    const { liquidacion } = orden
    contenido = (
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2 tarjeta p-4">
          <div className="flex flex-wrap items-center gap-3">
            <Placa placa={orden.placa} grande />
            <span className="font-medium">
              {orden.marca} {orden.modelo}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <ChipEstado estado={orden.estado} />
            {ultima && <span className="text-sm text-texto-suave">Actualizado {formatearFechaHora(ultima.fecha)}</span>}
          </div>
          <p className="text-base">{MENSAJES[orden.estado]}</p>
          {orden.estado === 'ENTREGADO' && (
            // Cambio #4B: el informe final solo existe cuando la orden fue entregada.
            <a
              href={`/api/v1/seguimiento/${codigo}/informe.pdf`}
              download
              className={claseBoton('primario', 'self-start')}
            >
              <Icono nombre="descargar" className="size-4" />
              Descargar informe PDF
            </a>
          )}
        </div>

        <div className="tarjeta p-4">
          <LineaTiempo estado={orden.estado} historial={etapas} />
        </div>

        {orden.estado !== 'CANCELADA' && (
          <section aria-labelledby="titulo-cobro" className="flex flex-col gap-3 tarjeta p-4">
            <h2 id="titulo-cobro" className="text-base font-semibold">
              Lo que se cobra
            </h2>
            {orden.servicios.length === 0 && orden.repuestos.length === 0 ? (
              <p className="text-sm text-texto-suave">Todavía no hay trabajos ni repuestos registrados.</p>
            ) : (
              <>
                <Lineas
                  titulo="Mano de obra"
                  lineas={orden.servicios.map((s) => ({ ...s, nombre: s.descripcion, unidad: '' }))}
                />
                <Lineas titulo="Repuestos" lineas={orden.repuestos} />
              </>
            )}
            <dl className="flex flex-col gap-1 border-t border-borde pt-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-texto-suave">Mano de obra</dt>
                <dd>{formatearPesos(liquidacion.mano_de_obra)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-texto-suave">Repuestos</dt>
                <dd>{formatearPesos(liquidacion.repuestos)}</dd>
              </div>
              <div className="flex justify-between text-lg font-semibold">
                <dt>Total</dt>
                <dd>{formatearPesos(liquidacion.total)}</dd>
              </div>
            </dl>
            <p className="text-xs text-texto-suave">Valores sin IVA. Pueden cambiar mientras el carro esté en el taller.</p>
          </section>
        )}

        <Boton variante="secundario" onClick={recargar} className="self-center">
          <Icono nombre="reloj" className="size-4" />
          Actualizar
        </Boton>
      </div>
    )
  }

  return (
    <div className="min-h-dvh bg-fondo">
      <header className="border-b border-borde bg-superficie px-4 py-3">
        <div className="mx-auto flex max-w-2xl items-center gap-2">
          <MarcaLogo className="size-8 shrink-0" />
          <div>
            <p className="font-semibold">{orden?.taller ?? 'Taller Digital'}</p>
            {orden && <p className="text-xs text-texto-suave">Orden #{orden.numero}</p>}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-2xl px-4 py-6">
        <h1 className="sr-only">Estado de su carro</h1>
        {contenido}
      </main>
    </div>
  )
}
