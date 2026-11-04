import { useState } from 'react'

import { api, erroresPorCampo } from '../../api/cliente.js'
import { formatearCantidad, formatearPesos, leerCantidad, leerPesos } from '../../formato.js'
import Boton from '../Boton.jsx'
import CampoFormulario from '../CampoFormulario.jsx'
import DialogoConfirmacion from '../DialogoConfirmacion.jsx'
import Icono from '../Icono.jsx'
import SelectorRepuesto from './SelectorRepuesto.jsx'

function FormularioServicio({ orden, alGuardar, alCancelar }) {
  const [datos, setDatos] = useState({ descripcion: '', precio: '', cantidad: '1' })
  const [errores, setErrores] = useState({})
  const [guardando, setGuardando] = useState(false)
  const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setGuardando(true)
    try {
      const actualizada = await api.post(`/ordenes/${orden.id}/servicios`, {
        descripcion: datos.descripcion,
        precio_unitario: leerPesos(datos.precio),
        cantidad: leerCantidad(datos.cantidad) || '1',
      })
      alGuardar(actualizada, `Mano de obra agregada: ${datos.descripcion.trim()}`)
    } catch (err) {
      const porCampo = erroresPorCampo(err)
      setErrores(Object.keys(porCampo).length ? porCampo : { general: err.message })
      setGuardando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-3 rounded-lg border border-borde bg-fondo p-3">
      <CampoFormulario
        etiqueta="Trabajo realizado"
        value={datos.descripcion}
        onChange={cambiar('descripcion')}
        error={errores.descripcion}
        placeholder="Cambio de pastillas, alineación…"
        maxLength={200}
        autoComplete="off"
        autoFocus
        obligatorio
      />
      <div className="grid grid-cols-2 gap-3">
        <CampoFormulario
          etiqueta="Valor (pesos)"
          inputMode="numeric"
          value={datos.precio}
          onChange={cambiar('precio')}
          error={errores.precio_unitario}
          placeholder="40.000"
          autoComplete="off"
          obligatorio
        />
        <CampoFormulario
          etiqueta="Cantidad"
          inputMode="decimal"
          value={datos.cantidad}
          onChange={cambiar('cantidad')}
          error={errores.cantidad}
          autoComplete="off"
        />
      </div>
      {errores.general && <p className="text-sm text-peligro">{errores.general}</p>}
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Boton variante="secundario" onClick={alCancelar} disabled={guardando}>
          Cancelar
        </Boton>
        <Boton type="submit" cargando={guardando}>
          Agregar
        </Boton>
      </div>
    </form>
  )
}

function FormularioRepuesto({ orden, alGuardar, alCancelar }) {
  const [repuesto, setRepuesto] = useState(null)
  const [cantidad, setCantidad] = useState('1')
  const [errores, setErrores] = useState({})
  const [guardando, setGuardando] = useState(false)

  async function enviar(evento) {
    evento.preventDefault()
    if (!repuesto) {
      setErrores({ repuesto_id: 'Elija un repuesto' })
      return
    }
    setErrores({})
    setGuardando(true)
    try {
      const actualizada = await api.post(`/ordenes/${orden.id}/repuestos`, {
        repuesto_id: repuesto.id,
        cantidad: leerCantidad(cantidad),
      })
      alGuardar(actualizada, `${repuesto.nombre} agregado; se descontó del inventario`)
    } catch (err) {
      const porCampo = erroresPorCampo(err)
      // 409 = no alcanza el stock: el mensaje dice cuánto queda.
      setErrores(Object.keys(porCampo).length ? porCampo : { cantidad: err.message })
      setGuardando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-3 rounded-lg border border-borde bg-fondo p-3">
      <SelectorRepuesto
        valor={repuesto}
        alCambiar={(elegido) => {
          setRepuesto(elegido)
          setErrores({})
        }}
        error={errores.repuesto_id}
      />
      <CampoFormulario
        etiqueta={`Cantidad${repuesto ? ` (${repuesto.unidad})` : ''}`}
        inputMode="decimal"
        value={cantidad}
        onChange={(e) => setCantidad(e.target.value)}
        error={errores.cantidad}
        ayuda="Se descuenta del inventario al agregarlo."
        autoComplete="off"
        obligatorio
      />
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Boton variante="secundario" onClick={alCancelar} disabled={guardando}>
          Cancelar
        </Boton>
        <Boton type="submit" cargando={guardando}>
          Agregar repuesto
        </Boton>
      </div>
    </form>
  )
}

function Lineas({ titulo, lineas, describir, editable, alQuitar, vacio }) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold">{titulo}</h3>
      {lineas.length === 0 ? (
        <p className="text-sm text-texto-suave">{vacio}</p>
      ) : (
        <ul className="divide-y divide-borde rounded-lg border border-borde">
          {lineas.map((linea) => {
            const { nombre, detalle } = describir(linea)
            return (
              <li key={linea.id} className="flex items-center gap-3 px-3 py-2 text-sm">
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{nombre}</p>
                  <p className="text-texto-suave">
                    {detalle} · {linea.registrador.nombre}
                  </p>
                </div>
                <span className="shrink-0 font-semibold">{formatearPesos(linea.subtotal)}</span>
                {editable && (
                  <button
                    type="button"
                    onClick={() => alQuitar(linea)}
                    className="rounded p-2 text-texto-suave hover:bg-peligro-suave hover:text-peligro"
                    aria-label={`Quitar ${nombre}`}
                  >
                    <Icono nombre="basura" className="size-4" />
                  </button>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

/** Mano de obra, repuestos y total de la orden (RF-09, RF-12). El total lo calcula el servidor. */
export default function PanelLiquidacion({ orden, alActualizar, alError }) {
  const [formulario, setFormulario] = useState(null)
  const [porQuitar, setPorQuitar] = useState(null)
  const [quitando, setQuitando] = useState(false)
  const editable = orden.puede_editar_trabajo
  const { liquidacion } = orden

  function guardado(actualizada, mensaje) {
    setFormulario(null)
    alActualizar(actualizada, mensaje)
  }

  async function quitar() {
    const { tipo, linea } = porQuitar
    setQuitando(true)
    try {
      const actualizada = await api.borrar(`/ordenes/${orden.id}/${tipo}/${linea.id}`)
      alActualizar(
        actualizada,
        tipo === 'repuestos' ? `${linea.repuesto.nombre} volvió al inventario` : 'Mano de obra quitada',
      )
    } catch (err) {
      alError(err.message)
    }
    setQuitando(false)
    setPorQuitar(null)
  }

  return (
    <section aria-labelledby="titulo-liquidacion" className="flex flex-col gap-4 tarjeta p-4">
      <h2 id="titulo-liquidacion" className="flex items-center gap-2 text-base font-semibold">
        <Icono nombre="pesos" className="size-5 text-texto-suave" />
        Mano de obra, repuestos y total
      </h2>

      <Lineas
        titulo="Mano de obra"
        lineas={orden.servicios}
        describir={(l) => ({
          nombre: l.descripcion,
          detalle: `${formatearCantidad(l.cantidad)} × ${formatearPesos(l.precio_unitario)}`,
        })}
        editable={editable}
        alQuitar={(linea) => setPorQuitar({ tipo: 'servicios', linea })}
        vacio="Sin mano de obra registrada."
      />
      <Lineas
        titulo="Repuestos"
        lineas={orden.repuestos}
        describir={(l) => ({
          nombre: l.repuesto.nombre,
          detalle: `${formatearCantidad(l.cantidad)} ${l.repuesto.unidad} × ${formatearPesos(l.precio_unitario)}`,
        })}
        editable={editable}
        alQuitar={(linea) => setPorQuitar({ tipo: 'repuestos', linea })}
        vacio="Sin repuestos usados."
      />

      {editable && formulario === 'servicio' && (
        <FormularioServicio orden={orden} alGuardar={guardado} alCancelar={() => setFormulario(null)} />
      )}
      {editable && formulario === 'repuesto' && (
        <FormularioRepuesto orden={orden} alGuardar={guardado} alCancelar={() => setFormulario(null)} />
      )}
      {editable && !formulario && (
        <div className="flex flex-col gap-2 sm:flex-row">
          <Boton variante="secundario" onClick={() => setFormulario('servicio')}>
            <Icono nombre="mas" />
            Mano de obra
          </Boton>
          <Boton variante="secundario" onClick={() => setFormulario('repuesto')}>
            <Icono nombre="mas" />
            Repuesto
          </Boton>
        </div>
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
      {orden.estado === 'CANCELADA' ? (
        <p className="text-sm text-texto-suave">
          Orden cancelada: no se cobra. Los repuestos volvieron al inventario.
        </p>
      ) : (
        <p className="text-xs text-texto-suave">Valores sin IVA.</p>
      )}

      <DialogoConfirmacion
        abierto={Boolean(porQuitar)}
        titulo={porQuitar?.tipo === 'repuestos' ? '¿Quitar este repuesto?' : '¿Quitar esta mano de obra?'}
        mensaje={
          porQuitar?.tipo === 'repuestos'
            ? `${porQuitar.linea.repuesto.nombre} vuelve al inventario y deja de cobrarse.`
            : 'Deja de cobrarse en esta orden.'
        }
        textoConfirmar="Quitar"
        variante="peligro"
        cargando={quitando}
        alConfirmar={quitar}
        alCancelar={() => setPorQuitar(null)}
      />
    </section>
  )
}
