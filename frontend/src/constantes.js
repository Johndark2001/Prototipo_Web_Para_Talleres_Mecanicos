export const ROLES = {
  ADMIN: 'ADMIN',
  RECEPCION: 'RECEPCION',
  MECANICO: 'MECANICO',
}

// Matriz de permisos (SPEC §3): el mecánico solo consulta clientes y vehículos.
export const ROLES_EDITAN_CLIENTES = [ROLES.ADMIN, ROLES.RECEPCION]

// Vocabulario del taller (RNF-08).
export const ETIQUETAS_ROL = {
  ADMIN: 'Administrador',
  RECEPCION: 'Recepción',
  MECANICO: 'Mecánico',
}

// Estados de la orden (SPEC §7) con su nombre en el taller. El ícono y el texto
// acompañan siempre al color (RNF-07).
export const ESTADOS_ORDEN = {
  RECIBIDO: { etiqueta: 'Recibido', icono: 'orden', clase: 'bg-primario-suave text-primario-oscuro' },
  EN_DIAGNOSTICO: { etiqueta: 'En diagnóstico', icono: 'buscar', clase: 'bg-aviso-suave text-aviso' },
  ESPERANDO_REPUESTOS: {
    etiqueta: 'Esperando repuestos',
    icono: 'reloj',
    clase: 'bg-peligro-suave text-peligro',
  },
  REPARADO: { etiqueta: 'Reparado', icono: 'llave', clase: 'bg-exito-suave text-exito' },
  ENTREGADO: { etiqueta: 'Entregado', icono: 'check', clase: 'bg-fondo text-texto-suave' },
  CANCELADA: { etiqueta: 'Cancelada', icono: 'cerrar', clase: 'bg-fondo text-texto-suave' },
}

// Tipo de vehículo (migración 0006). El ícono acompaña siempre al texto.
export const TIPOS_VEHICULO = {
  CARRO: { etiqueta: 'Carro', plural: 'carros', icono: 'carro' },
  MOTO: { etiqueta: 'Moto', plural: 'motos', icono: 'moto' },
}

// Formulario vacío de vehículo (alta del cliente con su primer vehículo, cambio #6).
export const VEHICULO_VACIO = { placa: '', tipo: 'CARRO', marca: '', modelo: '', anio: '', color: '' }

// Movimientos de inventario: el signo de la cantidad dice si entró o salió del estante.
export const TIPOS_MOVIMIENTO = {
  ENTRADA: 'Entrada',
  SALIDA: 'Salida a orden',
  AJUSTE: 'Ajuste por conteo',
  DEVOLUCION: 'Devolución',
}

// Sugerencias para el campo unidad; se puede escribir otra.
export const UNIDADES = ['unidad', 'litro', 'galón', 'juego', 'kit', 'metro', 'par']

// Texto del botón que lleva la orden a cada estado.
export const ACCIONES_ESTADO = {
  EN_DIAGNOSTICO: 'Iniciar diagnóstico',
  ESPERANDO_REPUESTOS: 'Esperando repuestos',
  REPARADO: 'Marcar reparado',
  ENTREGADO: 'Entregar',
  CANCELADA: 'Cancelar orden',
}
