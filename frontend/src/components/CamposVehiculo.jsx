import { TIPOS_VEHICULO } from '../constantes.js'
import { normalizarPlaca } from '../formato.js'
import CampoFormulario from './CampoFormulario.jsx'
import Icono from './Icono.jsx'

/** Elección del tipo con dos opciones grandes (radios nativos: teclado y lector de pantalla). */
function SelectorTipo({ valor, alCambiar, error }) {
  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="mb-1 text-sm font-medium text-texto">Tipo de vehículo</legend>
      <div className="grid grid-cols-2 gap-2 sm:max-w-sm">
        {Object.entries(TIPOS_VEHICULO).map(([clave, { etiqueta, icono }]) => (
          <label
            key={clave}
            className={`flex min-h-12 cursor-pointer items-center gap-2 rounded-lg border px-3 text-sm transition-[background-color,border-color,color] duration-150 ease-salida has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-primario ${
              valor === clave
                ? 'border-primario bg-primario-suave font-semibold text-primario-oscuro'
                : 'border-borde bg-superficie font-medium text-texto-suave hover:border-texto-suave/40 hover:text-texto'
            }`}
          >
            <input
              type="radio"
              name="tipo"
              value={clave}
              checked={valor === clave}
              onChange={() => alCambiar(clave)}
              className="sr-only"
            />
            <Icono nombre={icono} />
            {etiqueta}
          </label>
        ))}
      </div>
      {error && <p className="text-sm text-peligro">{error}</p>}
    </fieldset>
  )
}

/**
 * Tipo, placa, marca, modelo, año y color. Lo usan el formulario del vehículo y el alta del
 * cliente con su primer vehículo (cambio #6).
 */
export default function CamposVehiculo({ datos, alCambiar, errores }) {
  const esMoto = datos.tipo === 'MOTO'
  const cambiar = (campo) => (evento) => alCambiar({ ...datos, [campo]: evento.target.value })

  return (
    <>
      <SelectorTipo valor={datos.tipo} alCambiar={(tipo) => alCambiar({ ...datos, tipo })} error={errores.tipo} />
      <div className="grid gap-4 sm:grid-cols-2">
        <CampoFormulario
          etiqueta="Placa"
          value={datos.placa}
          onChange={(e) => alCambiar({ ...datos, placa: e.target.value.toUpperCase() })}
          onBlur={() => alCambiar({ ...datos, placa: normalizarPlaca(datos.placa) })}
          error={errores.placa}
          ayuda="Sin espacios ni guiones. Se corrige sola al salir del campo."
          autoCapitalize="characters"
          autoComplete="off"
          maxLength={12}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Marca"
          value={datos.marca}
          onChange={cambiar('marca')}
          error={errores.marca}
          placeholder={esMoto ? 'Yamaha, AKT, Bajaj…' : 'Mazda, Chevrolet, Renault…'}
          maxLength={50}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Modelo"
          value={datos.modelo}
          onChange={cambiar('modelo')}
          error={errores.modelo}
          placeholder={esMoto ? 'FZ 2.0, NKD 125…' : '3, Spark GT, Logan…'}
          maxLength={50}
          obligatorio
        />
        <CampoFormulario
          etiqueta="Año"
          type="number"
          inputMode="numeric"
          min={1950}
          max={2100}
          value={datos.anio}
          onChange={cambiar('anio')}
          error={errores.anio}
        />
        <CampoFormulario
          etiqueta="Color"
          value={datos.color}
          onChange={cambiar('color')}
          error={errores.color}
          maxLength={30}
        />
      </div>
    </>
  )
}

