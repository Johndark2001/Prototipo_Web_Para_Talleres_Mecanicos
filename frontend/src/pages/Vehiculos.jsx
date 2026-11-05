import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import { conParametros } from '../api/cliente.js'
import Aviso from '../components/Aviso.jsx'
import EnlaceBoton from '../components/EnlaceBoton.jsx'
import EstadoVacio from '../components/EstadoVacio.jsx'
import EtiquetaActivo from '../components/EtiquetaActivo.jsx'
import EtiquetaTipo from '../components/EtiquetaTipo.jsx'
import Esqueleto from '../components/Esqueleto.jsx'
import FiltroTipoVehiculo from '../components/FiltroTipoVehiculo.jsx'
import Icono from '../components/Icono.jsx'
import Paginacion from '../components/Paginacion.jsx'
import Placa from '../components/Placa.jsx'
import { ROLES_EDITAN_CLIENTES, TIPOS_VEHICULO } from '../constantes.js'
import { describirVehiculo, normalizarPlaca } from '../formato.js'
import { useConsulta } from '../hooks/useConsulta.js'
import { useRetrasado } from '../hooks/useRetrasado.js'
import { useSesion } from '../sesion/contexto.js'

const TAMANO_PAGINA = 20

function FilaVehiculo({ vehiculo }) {
  return (
    <li>
      <Link
        to={`/vehiculos/${vehiculo.id}`}
        className="flex min-h-14 items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-fondo"
      >
        <Placa placa={vehiculo.placa} />
        <div className="min-w-0 flex-1">
          <p className="flex min-w-0 items-center gap-2">
            <span className="truncate font-medium">{describirVehiculo(vehiculo)}</span>
            <EtiquetaTipo tipo={vehiculo.tipo} />
          </p>
          <p className="truncate text-sm text-texto-suave">Cliente: {vehiculo.cliente.nombre}</p>
        </div>
        {!vehiculo.activo && <EtiquetaActivo activo={false} />}
        <Icono nombre="derecha" className="size-5 shrink-0 text-texto-suave" />
      </Link>
    </li>
  )
}

export default function Vehiculos() {
  const { sesion } = useSesion()
  const puedeEditar = ROLES_EDITAN_CLIENTES.includes(sesion.usuario.rol)
  const [parametros, setParametros] = useSearchParams()
  const placaUrl = parametros.get('placa') ?? ''
  const [texto, setTexto] = useState(placaUrl)
  // El buscador de la barra superior cambia ?placa= sin desmontar esta pantalla.
  const [placaPrevia, setPlacaPrevia] = useState(placaUrl)
  if (placaUrl !== placaPrevia) {
    setPlacaPrevia(placaUrl)
    setTexto(placaUrl)
  }
  const busqueda = useRetrasado(normalizarPlaca(texto))
  const verInactivos = parametros.get('inactivos') === '1'
  const tipo = TIPOS_VEHICULO[parametros.get('tipo')] ? parametros.get('tipo') : null
  // Palabra para los mensajes según el filtro: «vehículos», «carros» o «motos».
  const plural = tipo ? TIPOS_VEHICULO[tipo].plural : 'vehículos'
  const pagina = Number(parametros.get('pagina') ?? 1)

  const { datos, error, recargar } = useConsulta(
    conParametros('/vehiculos', {
      placa: busqueda,
      activo: verInactivos ? undefined : true,
      tipo: tipo ?? undefined,
      page: pagina,
      page_size: TAMANO_PAGINA,
    }),
  )

  function cambiarParametros(cambios) {
    const nuevos = new URLSearchParams(parametros)
    for (const [clave, valor] of Object.entries(cambios)) {
      if (valor) nuevos.set(clave, valor)
      else nuevos.delete(clave)
    }
    setParametros(nuevos, { replace: true })
  }

  function escribir(evento) {
    const valor = evento.target.value.toUpperCase()
    setTexto(valor)
    setPlacaPrevia(normalizarPlaca(valor))
    cambiarParametros({ placa: normalizarPlaca(valor), pagina: null })
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      {/* Cambio #6: sin botón «+ Vehículo»; se registran con el cliente o desde su ficha. */}
      <h1 className="text-2xl font-semibold">Vehículos</h1>

      <div className="flex flex-col gap-2 lg:flex-row lg:items-center">
        <FiltroTipoVehiculo
          valor={tipo}
          alCambiar={(nuevo) => cambiarParametros({ tipo: nuevo, pagina: null })}
        />
        <label htmlFor="filtro-placa" className="sr-only">
          Buscar por placa
        </label>
        <input
          id="filtro-placa"
          type="search"
          value={texto}
          onChange={escribir}
          placeholder="Placa completa o una parte, p. ej. ABC o 123"
          autoComplete="off"
          autoCapitalize="characters"
          maxLength={12}
          className="min-h-11 w-full rounded-lg border border-borde bg-superficie px-3 font-mono text-base uppercase placeholder:font-sans placeholder:normal-case sm:max-w-md sm:text-sm"
        />
        <label className="inline-flex min-h-11 items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={verInactivos}
            onChange={(e) => cambiarParametros({ inactivos: e.target.checked ? '1' : null, pagina: null })}
            className="size-4"
          />
          Incluir inactivos
        </label>
      </div>

      {error && (
        <Aviso tipo="error">
          {error.message}{' '}
          <button type="button" onClick={recargar} className="font-semibold underline">
            Reintentar
          </button>
        </Aviso>
      )}

      {!datos && !error && <Esqueleto etiqueta="Cargando vehículos" />}

      {datos?.data.length === 0 &&
        (busqueda ? (
          <EstadoVacio
            icono="buscar"
            titulo={`No hay ${plural} con la placa «${busqueda}»`}
            texto={puedeEditar ? 'Si es un vehículo nuevo en el taller, regístrelo.' : undefined}
          >
            {puedeEditar && (
              <EnlaceBoton to="/vehiculos/nuevo" state={{ placa: busqueda, tipo: tipo ?? undefined }}>
                <Icono nombre="mas" />
                Registrar {busqueda}
              </EnlaceBoton>
            )}
          </EstadoVacio>
        ) : (
          <EstadoVacio
            icono={tipo ? TIPOS_VEHICULO[tipo].icono : 'carro'}
            titulo={`Aún no hay ${plural} ${tipo === 'MOTO' ? 'registradas' : 'registrados'}`}
            texto="Cada vehículo se registra a nombre de un cliente. Use «Nuevo cliente» o «Agregar vehículo» en la ficha del cliente."
          />
        ))}

      {datos?.data.length > 0 && (
        <ul className="divide-y divide-borde tarjeta">
          {datos.data.map((vehiculo) => (
            <FilaVehiculo key={vehiculo.id} vehiculo={vehiculo} />
          ))}
        </ul>
      )}

      <Paginacion
        paginacion={datos?.pagination}
        alCambiar={(nueva) => cambiarParametros({ pagina: nueva > 1 ? String(nueva) : null })}
      />
    </div>
  )
}
