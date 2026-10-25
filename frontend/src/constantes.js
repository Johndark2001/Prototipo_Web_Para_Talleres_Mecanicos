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
