import { useId, useState } from 'react'

import { TIPOS_VEHICULO } from '../../constantes.js'
import { useConsulta } from '../../hooks/useConsulta.js'
import { OTRO, claveBusqueda as clave } from '../../problema.js'
import Boton from '../Boton.jsx'
import CampoFormulario from '../CampoFormulario.jsx'
import Icono from '../Icono.jsx'

/** Buscador de la categoría del problema; la lista depende del tipo de vehículo. */
function SelectorCategoria({ tipo, valor, alCambiar, error }) {
  const id = useId()
  const [texto, setTexto] = useState('')
  const { datos: catalogo, error: errorCatalogo, recargar } = useConsulta('/catalogos/categorias-problema')
  const lista = tipo && catalogo ? catalogo[tipo] ?? [] : []
  const coincidencias = lista.filter((c) => clave(c).includes(clave(texto)))
  const idDescripcion = `${id}-descripcion`

  function elegir(categoria) {
    alCambiar(categoria)
    setTexto('')
  }

  function teclear(evento) {
    // Enter elige la primera coincidencia en vez de enviar el formulario.
    if (evento.key === 'Enter') {
      evento.preventDefault()
      if (texto.trim() && coincidencias.length > 0) elegir(coincidencias[0])
    }
  }

  return (
    <fieldset className="flex flex-col gap-1" aria-describedby={idDescripcion}>
      <legend className="mb-1 text-sm font-medium">
        Categoría del problema
        <span className="text-peligro" aria-hidden="true">
          {' '}
          *
        </span>
      </legend>

      {valor ? (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-borde bg-fondo px-3 py-2">
          <p className="flex min-w-0 items-center gap-2 font-medium">
            <Icono nombre="llave" className="size-4 shrink-0 text-texto-suave" />
            <span className="truncate">{valor}</span>
          </p>
          <Boton variante="texto" onClick={() => alCambiar('')}>
            Cambiar
          </Boton>
        </div>
      ) : !tipo ? (
        <p className="rounded-lg border border-dashed border-borde px-3 py-2 text-sm text-texto-suave">
          Elija primero el vehículo: las categorías dependen de si es carro o moto.
        </p>
      ) : (
        <>
          <label htmlFor={id} className="sr-only">
            Buscar categoría
          </label>
          <input
            id={id}
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            onKeyDown={teclear}
            placeholder="Escriba para buscar, p. ej. «fren» o «bateria»"
            autoComplete="off"
            aria-invalid={Boolean(error)}
            aria-controls={`${id}-lista`}
            className={`min-h-11 w-full rounded-lg border bg-superficie px-3 text-base sm:text-sm ${
              error ? 'border-peligro' : 'border-borde'
            }`}
          />
          {errorCatalogo ? (
            <p className="py-2 text-sm text-peligro">
              No se pudieron cargar las categorías.{' '}
              <button type="button" onClick={recargar} className="font-semibold underline">
                Reintentar
              </button>
            </p>
          ) : !catalogo ? (
            <p className="py-2 text-sm text-texto-suave">Cargando categorías…</p>
          ) : (
            <div aria-live="polite" className="text-sm">
              {coincidencias.length === 0 ? (
                <p className="py-2 text-texto-suave">
                  Ninguna categoría coincide con «{texto}». Elija «{OTRO}» y descríbalo.{' '}
                  <button type="button" onClick={() => elegir(OTRO)} className="font-semibold text-primario underline">
                    Usar «{OTRO}»
                  </button>
                </p>
              ) : (
                <ul
                  id={`${id}-lista`}
                  aria-label={`Categorías para ${TIPOS_VEHICULO[tipo]?.plural ?? 'vehículos'}`}
                  className="max-h-60 divide-y divide-borde overflow-y-auto overscroll-contain rounded-lg border border-borde"
                >
                  {coincidencias.map((categoria) => (
                    <li key={categoria}>
                      <button
                        type="button"
                        onClick={() => elegir(categoria)}
                        className="flex min-h-11 w-full items-center px-3 py-2 text-left transition-colors duration-150 hover:bg-fondo"
                      >
                        {categoria}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}

      <div id={idDescripcion}>{error && <p className="text-sm text-peligro">{error}</p>}</div>
    </fieldset>
  )
}

/**
 * Lo que registra recepción sobre el problema (cambio #5): categoría del catálogo, el detalle
 * cuando es «Otro» y la observación tal como la cuenta el cliente.
 */
export default function CamposProblema({ tipo, datos, alCambiar, errores }) {
  const esOtro = datos.categoria_problema === OTRO
  return (
    <div className="flex flex-col gap-4">
      <SelectorCategoria
        tipo={tipo}
        valor={datos.categoria_problema}
        alCambiar={(valor) => alCambiar('categoria_problema', valor)}
        error={errores.categoria_problema}
      />
      {esOtro && (
        <CampoFormulario
          etiqueta="Describa el problema"
          value={datos.categoria_otro}
          onChange={(e) => alCambiar('categoria_otro', e.target.value)}
          error={errores.categoria_otro}
          placeholder="P. ej. «Vidrio eléctrico no sube»"
          maxLength={120}
          obligatorio
        />
      )}
      <CampoFormulario
        etiqueta="Observación reportada por el cliente"
        error={errores.observacion_cliente}
        ayuda="Escriba lo que el cliente cuenta, con sus palabras."
      >
        {(props) => (
          <textarea
            {...props}
            value={datos.observacion_cliente}
            onChange={(e) => alCambiar('observacion_cliente', e.target.value)}
            rows={3}
            maxLength={2000}
            placeholder="El cliente indica que escucha un ruido metálico al frenar."
            className={`${props.className} py-2`}
          />
        )}
      </CampoFormulario>
    </div>
  )
}

