import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { api, conParametros, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CambioActivo from '../components/CambioActivo.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import EtiquetaStock from '../components/EtiquetaStock.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import Icono from '../components/Icono.jsx'
import Paginacion from '../components/Paginacion.jsx'
import { TIPOS_MOVIMIENTO } from '../constantes.js'
import { formatearCantidad, formatearFechaHora, formatearPesos, leerCantidad } from '../formato.js'
import { useAvisoNavegacion } from '../hooks/useAvisoNavegacion.js'
import { useConsulta } from '../hooks/useConsulta.js'

const TEXTOS = {
  ENTRADA: {
    titulo: 'Registrar entrada de mercancía',
    campo: 'cantidad',
    etiqueta: 'Cantidad que entró',
    ayuda: 'Se suma al stock actual.',
    nota: 'Nota (opcional)',
    placeholderNota: 'Proveedor o número de factura',
    boton: 'Registrar entrada',
  },
  AJUSTE: {
    titulo: 'Ajustar por conteo físico',
    campo: 'stock_contado',
    etiqueta: 'Cantidad contada en el estante',
    ayuda: 'El stock queda igual a lo que contó; la diferencia queda registrada.',
    nota: 'Motivo del ajuste',
    placeholderNota: 'Conteo de fin de mes, daño, pérdida…',
    boton: 'Guardar ajuste',
  },
}

function FormularioMovimiento({ tipo, repuesto, alGuardar, alCancelar }) {
  const textos = TEXTOS[tipo]
  const [cantidad, setCantidad] = useState('')
  const [nota, setNota] = useState('')
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    setGuardando(true)
    try {
      const actualizado = await api.post(`/repuestos/${repuesto.id}/movimientos`, {
        tipo,
        [textos.campo]: leerCantidad(cantidad) || null,
        nota,
      })
      alGuardar(actualizado)
    } catch (err) {
      const porCampo = erroresPorCampo(err)
      setErrores(porCampo)
      if (Object.keys(porCampo).length === 0) setErrorGeneral(err.message)
      setGuardando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-3 rounded-lg border border-primario/30 bg-primario-suave/40 p-4">
      <h2 className="text-base font-semibold">{textos.titulo}</h2>
      {errorGeneral && <Aviso tipo="error">{errorGeneral}</Aviso>}
      <div className="grid gap-3 sm:grid-cols-2">
        <CampoFormulario
          etiqueta={`${textos.etiqueta} (${repuesto.unidad})`}
          inputMode="decimal"
          value={cantidad}
          onChange={(e) => setCantidad(e.target.value)}
          error={errores[textos.campo]}
          ayuda={textos.ayuda}
          autoComplete="off"
          autoFocus
          obligatorio
        />
        <CampoFormulario
          etiqueta={textos.nota}
          value={nota}
          onChange={(e) => setNota(e.target.value)}
          error={errores.nota}
          placeholder={textos.placeholderNota}
          maxLength={1000}
          autoComplete="off"
          obligatorio={tipo === 'AJUSTE'}
        />
      </div>
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Boton variante="secundario" onClick={alCancelar} disabled={guardando}>
          Cancelar
        </Boton>
        <Boton type="submit" cargando={guardando}>
          {textos.boton}
        </Boton>
      </div>
    </form>
  )
}

function Movimientos({ repuesto }) {
  const [pagina, setPagina] = useState(1)
  const { datos, error, recargar } = useConsulta(
    conParametros(`/repuestos/${repuesto.id}/movimientos`, { page: pagina, page_size: 15 }),
  )

  if (error) {
    return (
      <Aviso tipo="error">
        {error.message}{' '}
        <button type="button" onClick={recargar} className="font-semibold underline">
          Reintentar
        </button>
      </Aviso>
    )
  }
  if (!datos) return <Esqueleto etiqueta="Cargando movimientos" />
  if (datos.data.length === 0) {
    return <p className="text-sm text-texto-suave">Todavía no hay movimientos de este repuesto.</p>
  }
  return (
    <div className="flex flex-col gap-3">
      <ul className="divide-y divide-borde rounded-lg border border-borde bg-superficie">
        {datos.data.map((m) => {
          const entra = Number(m.cantidad) > 0
          return (
            <li key={m.id} className="flex items-start gap-3 px-4 py-3 text-sm">
              <span className={`w-16 shrink-0 text-right font-mono font-semibold ${entra ? 'text-exito' : 'text-peligro'}`}>
                {entra ? '+' : '−'}
                {formatearCantidad(Math.abs(Number(m.cantidad)))}
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-medium">
                  {TIPOS_MOVIMIENTO[m.tipo]}
                  {m.orden && (
                    <>
                      {' '}
                      <Link to={`/ordenes/${m.orden.id}`} className="text-primario underline">
                        orden #{m.orden.numero}
                      </Link>
                    </>
                  )}
                </p>
                <p className="text-texto-suave">
                  {formatearFechaHora(m.fecha)} · {m.usuario.nombre}
                  {m.nota && ` · ${m.nota}`}
                </p>
              </div>
              <span className="shrink-0 text-texto-suave">
                quedan {formatearCantidad(m.stock_resultante)}
              </span>
            </li>
          )
        })}
      </ul>
      <Paginacion paginacion={datos.pagination} alCambiar={setPagina} />
    </div>
  )
}

function Dato({ etiqueta, children }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-texto-suave">{etiqueta}</dt>
      <dd className="font-medium">{children}</dd>
    </div>
  )
}

export default function RepuestoDetalle() {
  const { id } = useParams()
  const { datos: cargado, error, cargando, recargar } = useConsulta(`/repuestos/${id}`)
  const [repuesto, setRepuesto] = useState(null)
  const [formulario, setFormulario] = useState(null)
  const [version, setVersion] = useState(0)
  const [aviso, setAviso] = useAvisoNavegacion()

  if (error) return <ErrorCarga error={error} recurso="repuesto" alReintentar={recargar} />
  if (!cargado || cargando) return <Esqueleto etiqueta="Cargando repuesto" />
  // Tras un movimiento se muestra la respuesta del servidor sin volver a consultar.
  const actual = repuesto?.id === cargado.id ? repuesto : cargado

  function aplicar(actualizado, mensaje) {
    setRepuesto(actualizado)
    setFormulario(null)
    setVersion((v) => v + 1)
    setAviso(mensaje)
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <Link to="/inventario" className="inline-flex items-center gap-1 self-start text-sm text-texto-suave hover:underline">
        <Icono nombre="atras" className="size-4" />
        Inventario
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <h1 className="text-2xl font-semibold">{actual.nombre}</h1>
          <p className="font-mono text-sm text-texto-suave">{actual.codigo}</p>
          <div className="flex flex-wrap gap-2">
            <EtiquetaStock repuesto={actual} />
            <EtiquetaActivo activo={actual.activo} />
          </div>
        </div>
        <div className="flex gap-2">
          <EnlaceBoton to={`/inventario/${actual.id}/editar`} variante="secundario">
            <Icono nombre="lapiz" className="size-4" />
            Editar
          </EnlaceBoton>
          <CambioActivo
            ruta={`/repuestos/${actual.id}`}
            activo={actual.activo}
            nombre={`el repuesto ${actual.codigo}`}
            mensajeDesactivar="No se podrá agregar a nuevas órdenes. Su historial y su stock se conservan."
            alCambiar={(actualizado, mensaje) => {
              if (actualizado) setRepuesto(actualizado)
              setAviso(mensaje)
            }}
          />
        </div>
      </div>

      {aviso && (
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso(null)}>
          {aviso.texto}
        </Aviso>
      )}

      <dl className="grid grid-cols-2 gap-4 rounded-lg border border-borde bg-superficie p-4 sm:grid-cols-4">
        <Dato etiqueta="Stock">
          {formatearCantidad(actual.stock_actual)} {actual.unidad}
        </Dato>
        <Dato etiqueta="Mínimo">{formatearCantidad(actual.stock_minimo)}</Dato>
        <Dato etiqueta="Precio">{formatearPesos(actual.precio_venta)}</Dato>
        <Dato etiqueta="Unidad">{actual.unidad}</Dato>
      </dl>

      {formulario ? (
        <FormularioMovimiento
          key={formulario}
          tipo={formulario}
          repuesto={actual}
          alCancelar={() => setFormulario(null)}
          alGuardar={(actualizado) =>
            aplicar(actualizado, {
              tipo: 'exito',
              texto: `Stock de ${actualizado.nombre}: ${formatearCantidad(actualizado.stock_actual)} ${actualizado.unidad}`,
            })
          }
        />
      ) : (
        actual.activo && (
          <div className="flex flex-col gap-2 sm:flex-row">
            <Boton onClick={() => setFormulario('ENTRADA')}>
              <Icono nombre="mas" />
              Registrar entrada
            </Boton>
            <Boton variante="secundario" onClick={() => setFormulario('AJUSTE')}>
              Ajustar por conteo
            </Boton>
          </div>
        )
      )}

      <h2 className="text-lg font-semibold">Movimientos</h2>
      {/* Tras cada entrada o ajuste se vuelve a montar: consulta de nuevo desde la página 1. */}
      <Movimientos key={version} repuesto={actual} />
    </div>
  )
}
