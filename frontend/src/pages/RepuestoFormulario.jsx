import { useId, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'

import { api, erroresPorCampo } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import Boton from '../components/Boton.jsx'
import CampoFormulario from '../components/CampoFormulario.jsx'
import ErrorCarga from '../components/ErrorCarga.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import { UNIDADES } from '../constantes.js'
import { leerCantidad, leerPesos } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'

const VACIO = {
  codigo: '',
  nombre: '',
  unidad: 'unidad',
  precio_venta: '',
  stock_minimo: '',
  stock_inicial: '',
}

function Formulario({ inicial }) {
  const navegar = useNavigate()
  const idUnidades = useId()
  const esNuevo = !inicial.id
  const [datos, setDatos] = useState(
    esNuevo
      ? VACIO
      : {
          ...VACIO,
          codigo: inicial.codigo,
          nombre: inicial.nombre,
          unidad: inicial.unidad,
          // Sin separador de miles: "1.500" se leería como 1,5 al guardar.
          precio_venta: String(Number(inicial.precio_venta)),
          stock_minimo: String(Number(inicial.stock_minimo)),
        },
  )
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })
  const volverA = esNuevo ? '/inventario' : `/inventario/${inicial.id}`

  async function enviar(evento) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral(null)
    setGuardando(true)
    const cuerpo = {
      codigo: datos.codigo,
      nombre: datos.nombre,
      unidad: datos.unidad,
      precio_venta: leerPesos(datos.precio_venta),
      stock_minimo: leerCantidad(datos.stock_minimo) || '0',
    }
    if (esNuevo) cuerpo.stock_inicial = leerCantidad(datos.stock_inicial) || '0'
    try {
      const guardado = esNuevo
        ? await api.post('/repuestos', cuerpo)
        : await api.patch(`/repuestos/${inicial.id}`, cuerpo)
      navegar(`/inventario/${guardado.id}`, {
        state: { aviso: esNuevo ? `Repuesto ${guardado.nombre} registrado` : 'Cambios guardados' },
      })
    } catch (err) {
      setErrores(erroresPorCampo(err))
      setErrorGeneral(err.message)
      setGuardando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="flex flex-col gap-4 rounded-lg border border-borde bg-superficie p-4">
      {errorGeneral && <Aviso tipo="error">{errorGeneral}</Aviso>}
      <div className="grid gap-4 sm:grid-cols-2">
        <CampoFormulario
          etiqueta="Nombre"
          value={datos.nombre}
          onChange={cambiar('nombre')}
          error={errores.nombre}
          placeholder="Filtro de aceite Mann W712"
          autoComplete="off"
          obligatorio
        />
        <CampoFormulario
          etiqueta="Código"
          value={datos.codigo}
          onChange={cambiar('codigo')}
          error={errores.codigo}
          ayuda="Referencia del fabricante o la que use el taller. No se repite."
          autoComplete="off"
          autoCapitalize="characters"
          obligatorio
        />
        <CampoFormulario
          etiqueta="Precio de venta (pesos)"
          inputMode="numeric"
          value={datos.precio_venta}
          onChange={cambiar('precio_venta')}
          error={errores.precio_venta}
          placeholder="25.000"
          ayuda="Por unidad. Cambiarlo no altera las órdenes ya registradas."
          autoComplete="off"
          obligatorio
        />
        <div className="flex flex-col gap-1">
          <CampoFormulario
            etiqueta="Unidad"
            value={datos.unidad}
            onChange={cambiar('unidad')}
            error={errores.unidad}
            list={idUnidades}
            ayuda="Cómo se cuenta: unidad, litro, juego…"
            autoComplete="off"
            obligatorio
          />
          <datalist id={idUnidades}>
            {UNIDADES.map((unidad) => (
              <option key={unidad} value={unidad} />
            ))}
          </datalist>
        </div>
        <CampoFormulario
          etiqueta="Stock mínimo"
          inputMode="decimal"
          value={datos.stock_minimo}
          onChange={cambiar('stock_minimo')}
          error={errores.stock_minimo}
          placeholder="0"
          ayuda="Al llegar a esta cantidad, el sistema avisa que hay que pedir más."
          autoComplete="off"
        />
        {esNuevo && (
          <CampoFormulario
            etiqueta="Stock actual en el estante"
            inputMode="decimal"
            value={datos.stock_inicial}
            onChange={cambiar('stock_inicial')}
            error={errores.stock_inicial}
            placeholder="0"
            ayuda="Queda registrado como la primera entrada del repuesto."
            autoComplete="off"
          />
        )}
      </div>
      {!esNuevo && (
        <p className="text-sm text-texto-suave">
          El stock no se edita aquí: cambia con las entradas, los ajustes y las órdenes, y cada cambio queda registrado.
        </p>
      )}
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Link
          to={volverA}
          className="inline-flex min-h-11 items-center justify-center rounded-md border border-borde px-4 text-sm font-semibold hover:bg-fondo"
        >
          Cancelar
        </Link>
        <Boton type="submit" cargando={guardando}>
          {esNuevo ? 'Guardar repuesto' : 'Guardar cambios'}
        </Boton>
      </div>
    </form>
  )
}

export default function RepuestoFormulario() {
  const { id } = useParams()
  const { datos, error, recargar } = useConsulta(id ? `/repuestos/${id}` : null)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-2xl font-semibold">
        {id ? `Editar repuesto${datos ? `: ${datos.nombre}` : ''}` : 'Nuevo repuesto'}
      </h1>
      {!id && <Formulario inicial={{}} />}
      {id && error && <ErrorCarga error={error} recurso="repuesto" alReintentar={recargar} />}
      {id && !datos && !error && <Esqueleto etiqueta="Cargando repuesto" />}
      {id && datos && <Formulario key={datos.id} inicial={datos} />}
    </div>
  )
}
