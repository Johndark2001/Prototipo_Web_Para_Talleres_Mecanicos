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

// Texto del botón que lleva la orden a cada estado.
export const ACCIONES_ESTADO = {
  EN_DIAGNOSTICO: 'Iniciar diagnóstico',
  ESPERANDO_REPUESTOS: 'Esperando repuestos',
  REPARADO: 'Marcar reparado',
  ENTREGADO: 'Entregar',
  CANCELADA: 'Cancelar orden',
}
