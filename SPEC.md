# SPEC — Prototipo web de gestión operativa para talleres mecánicos (zona norte de Cali)

| Campo | Valor |
|---|---|
| Versión | 1.1 — Fase 0 cerrada |
| Fecha | 23/10/2026 |
| Estado | **APROBADO** por el autor el 23/10/2026. La Fase 0 queda cerrada. |
| Autor y único desarrollador | John Edison Hernández Vargas |
| Programa | Ingeniería de Software — Corporación Universitaria Iberoamericana |
| Decisiones técnicas | [docs/decisions/](docs/decisions/) (ADR-001 a ADR-006) |
| Modelo de datos | [docs/modelo-datos.md](docs/modelo-datos.md) · [docs/modelo-datos.dbml](docs/modelo-datos.dbml) |

Este documento es la referencia oficial para construir el MVP. Si el código y este SPEC no coinciden, se corrige primero el SPEC y después el código.

**Fuentes y su orden de prioridad:**

| Clave | Documento | Prioridad |
|---|---|---|
| D1 | `investigacion_completa.md` | 1 |
| D2 | `entrevistas_e_instrumentos.md` | 2 |
| D3 | `resumen_requerimientos.md` | 3 |
| — | Buenas prácticas de ingeniería de software | 4 |
| — | Buenas prácticas de UX/UI | 5 |

Lo que D1 y D3 describen como "implementado", "piloto" o "capacitación" se trata como **antecedente documental**. En este repositorio todavía no existe software (decisión P-3).

---

## 1. Objetivo

Construir un prototipo web (MVP) para talleres mecánicos pequeños y medianos, formales e informales, de las comunas 2, 4, 5 y 6 de Cali. El sistema les permite:

- registrar clientes y vehículos;
- recibir vehículos y llevar órdenes de trabajo con estados trazables;
- controlar el inventario de repuestos ligado a cada orden;
- liquidar la orden con el desglose de mano de obra y repuestos;
- consultar el historial de mantenimiento de cada vehículo;
- dar al cliente un enlace para seguir el estado de su vehículo;
- obtener reportes operativos, incluidos los tiempos de cada etapa.

**Para qué sirve en la tesis.** El sistema debe producir los datos con los que se responde la pregunta de investigación (D1 §1.1): el impacto en los tiempos de respuesta y en la eficiencia operativa. Por eso cada cambio de estado queda registrado con fecha, hora y usuario.

**Objetivos específicos a los que contribuye** (D1 §1.2.2):

| Clave | Objetivo específico |
|---|---|
| OE1 | Diagnosticar los procesos operativos actuales |
| OE2 | Diseñar la estructura y los módulos |
| OE3 | Implementar y evaluar con una prueba piloto |
| OE4 | Capacitar y recoger retroalimentación |

---

## 2. Alcance

### 2.1 Incluido

- Usuarios y roles.
- Clientes y vehículos.
- Recepción del vehículo con apertura de la orden.
- Órdenes de trabajo con estados y mecánico asignado.
- Mano de obra y repuestos registrados en la orden.
- Inventario: entradas, salidas, ajustes, devoluciones y alertas de stock.
- Liquidación de la orden, sin IVA.
- Historial de mantenimiento del vehículo.
- Seguimiento público por enlace.
- Dashboard y reportes.
- Interfaz pensada primero para el celular.
- Varios talleres en una sola instalación, con sus datos separados lógicamente (multi-tenant).

### 2.2 Excluido (no se construye en este MVP)

- Facturación electrónica DIAN, IVA y cualquier requisito tributario.
- Pagos en línea.
- Cuentas de cliente con usuario y contraseña.
- Notificaciones automáticas por SMS, correo o API de WhatsApp.
- Funcionamiento sin conexión y app nativa.
- Fotos y archivos adjuntos.
- Proveedores, compras, contabilidad y nómina.
- Varias sedes por taller.
- Indicadores MTBF y MTTR.
- Inteligencia artificial.
- Pantalla de superadministración. Los talleres y su primer administrador los crea el desarrollador con un script (ver ADR-006).

### 2.3 Limitaciones

- Es un MVP académico, sin garantía de disponibilidad.
- Requiere conexión a internet.
- Se aloja en planes gratuitos (P-6). La primera solicitud después de un rato de inactividad puede tardar varios segundos (ver R-07).
- Está dimensionado para el volumen de un piloto: decenas de usuarios y miles de órdenes.

---

## 3. Usuarios, roles y permisos

| Perfil | Rol | Dispositivo principal | Qué necesita |
|---|---|---|---|
| Dueño, administrador o gerente | `ADMIN` | PC y celular | Visión global, inventario, usuarios y reportes |
| Recepcionista o asesor | `RECEPCION` | PC | Recibir vehículos, informar al cliente y entregar |
| Mecánico (usuario propio, P-7) | `MECANICO` | Celular | Ver sus órdenes, diagnosticar, cambiar el estado y registrar trabajo y repuestos |
| Cliente final | Sin cuenta (P-4) | Celular | Ver el estado y la liquidación de su orden |

En un taller sin recepcionista, el usuario `ADMIN` hace también las tareas de recepción.

**Matriz de permisos.** Todas las acciones se limitan siempre al taller del usuario.

| Acción | ADMIN | RECEPCION | MECANICO |
|---|---|---|---|
| Gestionar los usuarios del taller | ✓ | — | — |
| Crear y editar clientes y vehículos | ✓ | ✓ | solo ver |
| Abrir una orden (recepción) y asignar o reasignar mecánico | ✓ | ✓ | — |
| Ver órdenes | todas | todas | solo las asignadas a él |
| Registrar diagnóstico, trabajo, servicios y repuestos | ✓ | ✓ | solo en sus órdenes |
| Cambiar el estado de una orden (ver §7) | todos los cambios | entregar y cancelar | cambios de taller en sus órdenes |
| Devolver una orden al estado anterior (con nota) | ✓ | — | — |
| Catálogo de repuestos, entradas y ajustes de inventario | ✓ | — | — |
| Consultar el inventario | ✓ | ✓ | ✓ |
| Catálogo de servicios | ✓ | — | — |
| Dashboard | ✓ | ✓ | vista "Mis órdenes" |
| Reportes | ✓ | — | — |

---

## 4. Requisitos funcionales

Prioridad según el método MoSCoW: *Must* (obligatorio), *Should* (importante), *Could* (deseable). La columna "Fuente" indica de qué documento sale la evidencia.

| ID | Requisito | Problema que resuelve | Fuente | Obj. | Prioridad |
|---|---|---|---|---|---|
| RF-01 | Inicio y cierre de sesión | Proteger el acceso a datos personales | D1 glosario (Gestión de usuarios); §3.6 | OE2, OE3 | Must |
| RF-02 | Roles ADMIN, RECEPCION y MECANICO con la matriz de §3 | Que cada persona vea solo lo que le corresponde | D1 glosario (RBAC) | OE2 | Must |
| RF-03 | Gestión de clientes con búsqueda y autorización de tratamiento de datos | Datos dispersos; cumplimiento de la Ley 1581 | D1 §4.2; D2; D1 §3.6 | OE2, OE3 | Must |
| RF-04 | Gestión de vehículos ligados al cliente, con placa única por taller | Historial difícil de encontrar | D3 (Arquitectura); D1 §4.2 | OE2, OE3 | Must |
| RF-05 | Recepción: abrir la orden a partir de la placa, con motivo de ingreso y kilometraje | Cuellos de botella al recibir vehículos | D1 §1.1, §1.3; D3 (Introducción) | OE3 | Must |
| RF-06 | Estados de la orden según §7. Cada cambio queda registrado con fecha, usuario y nota | Seguimiento del servicio; medición de tiempos | D1 Tabla 2; D3; P-5 | OE2, OE3 | Must |
| RF-07 | Asignar y reasignar mecánico, con historial de asignaciones, y vista "Mis órdenes" | Asignación empírica; información que se pierde entre recepción y mecánico | D1 Cap. 1, §3.2.3; P-7 | OE3 | Must |
| RF-08 | Catálogo de repuestos con stock actual, stock mínimo, entradas y ajustes | Conteo manual | D1 Tabla 2 | OE3 | Must |
| RF-09 | Registrar en la orden los repuestos usados, con descuento automático del stock | No se sabe qué se consume | D1 Tabla 2; D3 | OE3 | Must |
| RF-10 | Alertas de stock mínimo en el dashboard y en el inventario | Faltan insumos sin aviso | D1 Tabla 2; D3 | OE3 | Must |
| RF-11 | Historial de mantenimiento por vehículo | Pérdida del historial | D1 §4.2; D2; D3 | OE3 | Must |
| RF-12 | Liquidación de la orden: servicios + repuestos = total, sin IVA | Cobros poco transparentes | D1 §1.3; D2; D3; P-9 | OE3 | Must |
| RF-13 | Página pública de seguimiento con enlace único: estado, línea de tiempo y liquidación | El 85 % de los encuestados pide un canal digital | D2; D3 (tabla); P-4 | OE3 | Must |
| RF-14 | Dashboard con órdenes por estado, órdenes del día y alertas de stock | Falta de visión global del taller | D1 §3.2.3 | OE3 | Must |
| RF-15 | Reportes: **R1** órdenes por estado, período y mecánico; **R2** tiempo promedio por etapa (incluida ESPERANDO_REPUESTOS) y tiempo total de ingreso a entrega; **R3** repuestos más consumidos; **R4** repuestos con stock bajo | Decidir con datos; medir el piloto | D1 §4.2, §7.3; D3; P-5 | OE3 | Must |
| RF-16 | Gestión de usuarios del taller por el ADMIN: crear, desactivar y cambiar rol | Sin esto no se pueden crear los mecánicos | D1 glosario; P-7 | OE2 | Must |
| RF-17 | Interfaz pensada primero para el celular, con íconos, botones rápidos y lenguaje del taller | Resistencia al cambio | D1 Tabla 2; D2; D3 | OE2, OE3 | Must |
| RF-18 | Catálogo de servicios de mano de obra con precio de referencia | Estandarizar precios y trabajos | D1 §2.1 (Guerrero) | OE2 | Should |
| RF-19 | El enlace del cliente muestra también el historial del vehículo, solo de la titularidad actual (RN-21) | Respaldar el valor de reventa | D3 | OE3 | Should |
| RF-20 | Botón "Enviar por WhatsApp" que abre un mensaje con el enlace ya escrito (sin API) | Notificar al cliente sin costo | D1 §1.3; D3 | OE3 | Should |
| RF-21 | Manual de usuario y guía rápida | Capacitación | D1 OE4; §4.4 | OE4 | Should |
| RF-22 | Exportar reportes a CSV | Usar los datos fuera del sistema | D1 §4.2 | OE3 | Could |
| RF-23 | Liquidación imprimible | Dar un comprobante al cliente | D1 §1.3 | OE3 | Could |
| RF-24 | Lista de verificación al recibir el vehículo (combustible, daños visibles) | Evitar disputas al entregar | D1 §3.4.1 | OE3 | Could |
| RF-25 | Recordatorio de próximo mantenimiento por fecha o kilometraje | Mantenimiento preventivo | D3; D1 glosario | OE3 | Could |
| RF-26 | Agendamiento de citas | Demanda sin turnos | D1 §3.2.3, §3.5.2 | — | Could |

**Won't have (fuera de alcance):** todo lo listado en §2.2.

Las funciones *Could* (RF-22 a RF-26) no tienen modelo de datos en esta versión. Si se aprueban, se agregan con un ADR nuevo o con una actualización del modelo.

---

## 5. Requisitos no funcionales

| ID | Requisito | Criterio verificable |
|---|---|---|
| RNF-01 | Uso en celular | Todas las pantallas funcionan desde 360 px de ancho sin desplazamiento horizontal |
| RNF-02 | Eficiencia | Abrir una orden de un vehículo ya registrado toma 3 pasos o menos y menos de 2 minutos para un usuario capacitado. Se mide en el piloto. |
| RNF-03 | Rendimiento | Los listados responden en menos de 2 s con conexión 4G, con hasta 5.000 órdenes por taller y páginas de 20 |
| RNF-04 | Seguridad | Contraseñas con hash argon2id, HTTPS, sesión en cookie httpOnly y permisos verificados en cada solicitud (ADR-005) |
| RNF-05 | Aislamiento entre talleres | Un usuario nunca lee ni modifica datos de otro taller. Cada recurso tiene una prueba automatizada que lo comprueba (ADR-006). |
| RNF-06 | Ley 1581 | La autorización de datos queda registrada con fecha, se piden solo los datos personales necesarios y existe la anonimización |
| RNF-07 | Accesibilidad | Contraste nivel AA, uso con teclado, etiquetas en los formularios y el estado nunca se indica solo con color |
| RNF-08 | Lenguaje | Vocabulario del taller: "placa", "carro", "repuesto", "mano de obra", "entregar" |
| RNF-09 | Mantenibilidad | Cada regla de negocio de §6 tiene al menos una prueba automatizada |
| RNF-10 | Portabilidad | La configuración se lee solo de variables de entorno y no se usan funciones propias de un proveedor (ADR-001) |
| RNF-11 | Costo | $0 de infraestructura durante el piloto y la sustentación (P-6) |

---

## 6. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | El estado de una orden solo cambia por las transiciones de §7. Cada cambio inserta un registro en `historial_estado_orden` con estado anterior, estado nuevo, usuario, fecha y nota. |
| RN-02 | Registrar un repuesto en una orden descuenta el stock y crea un movimiento `SALIDA` dentro de **una sola transacción**. Si no hay stock suficiente, la operación se rechaza: el stock nunca queda negativo. |
| RN-03 | Quitar un repuesto de una orden abierta, o cancelar la orden, devuelve el stock con un movimiento `DEVOLUCION`. |
| RN-04 | Si `stock_actual` queda igual o por debajo de `stock_minimo`, aparece una alerta visible. |
| RN-05 | Cada línea de la orden guarda una copia del precio unitario en el momento de registrarla. Cambiar el precio en el catálogo no altera órdenes existentes. |
| RN-06 | La liquidación la calcula el servidor como la suma de cantidad × precio de todas las líneas. No se guarda un total aparte ni se acepta un total enviado por el cliente. No hay IVA (P-9). |
| RN-07 | Una orden en `ENTREGADO` o `CANCELADA` ya no se puede modificar. |
| RN-08 | Un vehículo tiene como máximo una orden abierta, es decir, en un estado distinto de `ENTREGADO` y `CANCELADA`. |
| RN-09 | Toda lectura y escritura se limita al `taller_id` del usuario que inició sesión. Si se pide un recurso de otro taller, la respuesta es "no encontrado" (ADR-006). |
| RN-10 | No se registra un cliente sin su autorización de tratamiento de datos (`autoriza_datos = verdadero`, con fecha). |
| RN-11 | Las órdenes, el historial de estados, las asignaciones y los movimientos de inventario **nunca se borran**. Clientes, vehículos, repuestos, servicios y usuarios se **desactivan**. Si un cliente pide que se eliminen sus datos, sus datos personales se **anonimizan** y la historia operativa se conserva. |
| RN-12 | El número de orden es un consecutivo por taller que se asigna dentro de una transacción. El `codigo_seguimiento` es aleatorio, de al menos 128 bits, único e imposible de adivinar. |
| RN-13 | Para pasar de `RECIBIDO` a `EN_DIAGNOSTICO`, la orden debe tener un mecánico asignado. |
| RN-14 | Cada asignación o reasignación de mecánico inserta un registro en `asignacion_orden` (P-7). |
| RN-15 | Cada línea de servicio o de repuesto registra quién la creó (`registrado_por`). Cada movimiento de inventario registra su usuario (P-7). |
| RN-16 | Un mecánico solo trabaja en las órdenes que tiene asignadas. Para desactivar a un mecánico con órdenes abiertas, primero hay que reasignarlas. |
| RN-17 | Para pasar a `REPARADO`, el campo `trabajo_realizado` no puede estar vacío. |
| RN-18 | Para cancelar una orden se debe escribir un motivo. |
| RN-19 | Las cantidades de repuestos admiten decimales (por ejemplo, litros de aceite). Los montos en pesos se guardan como decimales exactos, nunca como números de coma flotante. |
| RN-20 | La placa se guarda normalizada: en mayúsculas, sin espacios ni guiones. |
| RN-21 | El historial que se ve en el enlace público incluye solo las órdenes del vehículo que pertenecen a su **titular actual**, y solo si ese titular es el mismo cliente de la orden consultada. Si el vehículo cambió de dueño, el enlace de una orden antigua muestra únicamente esa orden (H-4). |

---

## 7. Estados de la orden y transiciones permitidas (P-5)

```
RECIBIDO ──► EN_DIAGNOSTICO ──► ESPERANDO_REPUESTOS ──► REPARADO ──► ENTREGADO
                   │                                        ▲
                   └────────────────────────────────────────┘   (pasar a REPARADO sin esperar repuestos)

Cualquier estado excepto ENTREGADO o CANCELADA ──► CANCELADA
```

| Desde | Hacia | Quién puede | Condición |
|---|---|---|---|
| — | RECIBIDO | ADMIN, RECEPCION | Se crea la orden (RF-05) |
| RECIBIDO | EN_DIAGNOSTICO | Mecánico asignado, ADMIN | RN-13 |
| EN_DIAGNOSTICO | ESPERANDO_REPUESTOS | Mecánico asignado, ADMIN | Nota opcional indicando qué repuesto falta |
| EN_DIAGNOSTICO | REPARADO | Mecánico asignado, ADMIN | RN-17 |
| ESPERANDO_REPUESTOS | REPARADO | Mecánico asignado, ADMIN | RN-17 |
| REPARADO | ENTREGADO | ADMIN, RECEPCION | Se registra `fecha_entrega` |
| Cualquier estado no final | CANCELADA | ADMIN, RECEPCION | RN-18 y RN-03 |
| Estado no final | Estado anterior (un paso) | Solo ADMIN | Nota obligatoria. **Excepción:** no se permite volver de ESPERANDO_REPUESTOS a EN_DIAGNOSTICO (H-1). |

`ENTREGADO` y `CANCELADA` son estados finales.

**Decisión aprobada (H-1).** `ESPERANDO_REPUESTOS` es **opcional**. Hay dos flujos válidos:

- `RECIBIDO → EN_DIAGNOSTICO → REPARADO → ENTREGADO`
- `RECIBIDO → EN_DIAGNOSTICO → ESPERANDO_REPUESTOS → REPARADO → ENTREGADO`

**No** se permite volver de `ESPERANDO_REPUESTOS` a `EN_DIAGNOSTICO`. El ADMIN tampoco puede hacer ese retroceso: la regla de "un paso atrás" no aplica a esta transición.

**Métricas que salen del historial de estados (RF-15, reporte R2):**
- tiempo en cada etapa;
- tiempo total entre `RECIBIDO` y `ENTREGADO`;
- porcentaje de órdenes que pasaron por `ESPERANDO_REPUESTOS`;
- tiempo promedio de espera de repuestos.

---

## 8. Arquitectura y tecnologías

| Decisión | Selección | ADR |
|---|---|---|
| Arquitectura | Monolito cliente-servidor por capas, con API REST JSON. Un solo despliegue: el backend también sirve la interfaz compilada. | [ADR-001](docs/decisions/ADR-001-arquitectura.md) |
| Backend | Python 3.13 + FastAPI + SQLAlchemy 2 + Alembic + Pydantic | [ADR-002](docs/decisions/ADR-002-backend.md) |
| Base de datos | PostgreSQL 17 | [ADR-003](docs/decisions/ADR-003-base-de-datos.md) |
| Frontend | React + Vite + JavaScript + Tailwind CSS + React Router | [ADR-004](docs/decisions/ADR-004-frontend.md) |
| Autenticación | JWT firmado guardado en cookie httpOnly; el usuario se vuelve a cargar de la base en cada solicitud; seguimiento público con código aleatorio | [ADR-005](docs/decisions/ADR-005-autenticacion.md) |
| Varios talleres (multi-tenant) | Una base de datos y un esquema compartidos; `taller_id` en las tablas raíz; filtro obligatorio en la capa de servicios | [ADR-006](docs/decisions/ADR-006-multi-tenant.md) |

**Capas del backend.** Cada capa solo depende de la siguiente:
1. **API:** recibe las solicitudes, autentica y valida la entrada.
2. **Servicios:** aplica las reglas de negocio de §6 y el filtro por taller.
3. **Acceso a datos:** usa el ORM con consultas parametrizadas.
4. **Base de datos:** PostgreSQL.

**Despliegue (P-6).** La aplicación va en un servicio de plataforma (PaaS) con plan gratuito. La base de datos va en un PostgreSQL administrado con plan gratuito, en otro proveedor. Candidatos: Render y Neon. Las condiciones de esos planes se verifican en la Fase 8 (ver ADR-001).

---

## 9. Modelo de datos (resumen)

El modelo tiene 12 tablas.

- **Tablas raíz** (llevan `taller_id`): `taller`, `usuario`, `cliente`, `vehiculo`, `orden_trabajo`, `servicio` y `repuesto`.
- **Tablas hijas** (heredan el taller a través de su tabla padre):
  - de la orden: `historial_estado_orden`, `asignacion_orden`, `orden_servicio` y `orden_repuesto`;
  - del repuesto: `movimiento_inventario`.

**Entidades que no tienen tabla propia:**
- **Técnico:** es un `usuario` con rol `MECANICO`.
- **Factura:** la liquidación se calcula a partir de las líneas de la orden (RN-06).
- **Historial de mantenimiento:** es una consulta de las órdenes entregadas de un vehículo.

El detalle completo (cardinalidades, restricciones y diagramas) está en [docs/modelo-datos.md](docs/modelo-datos.md).

---

## 10. Convenciones de la API

Los endpoints concretos se definen y documentan en cada fase, mediante la documentación OpenAPI que genera FastAPI. Desde ya se fijan estas convenciones:

- **Rutas:** prefijo `/api/v1`. Los recursos se nombran en plural y sin verbos. Los subrecursos de una orden cuelgan de la orden.
- **Formato JSON:**
  - nombres de campo en `snake_case`;
  - fechas en ISO 8601 con zona horaria;
  - montos como texto decimal, para no perder precisión.
- **Listados:** paginados con `page` y `page_size` (máximo 100). Los filtros se pasan como parámetros de consulta.
- **Errores:** siempre con el mismo formato, `{"error": {"code": "...", "message": "...", "details": ...}}`. Los mensajes van en el español que se usa en el taller.

| Código | Significado |
|---|---|
| 401 | No ha iniciado sesión |
| 403 | Su rol no tiene permiso |
| 404 | No existe o pertenece a otro taller (la respuesta no distingue entre los dos casos) |
| 409 | Conflicto de estado o de stock |
| 422 | Datos inválidos |
| 429 | Demasiadas solicitudes |

- **Validación:** se hace solo en la entrada de la API, con esquemas Pydantic. La capa de servicios confía en los datos ya validados.
- **Página pública de seguimiento:**
  - sin autenticación y con límite de solicitudes;
  - muestra el nombre del taller, el número de orden, la placa enmascarada, marca y modelo, el estado, la línea de tiempo y la liquidación;
  - nunca muestra documento, teléfono ni correo.

---

## 11. Experiencia de usuario

**Flujos críticos:**

1. **Recepción**
   1. Buscar la placa.
   2. Si no existe, registrar cliente y vehículo, con la autorización de datos.
   3. Escribir el motivo de ingreso y el kilometraje.
   4. Asignar un mecánico.
   5. Crear la orden en estado `RECIBIDO`.
   6. Enviar el enlace por WhatsApp.
2. **Taller**
   1. El mecánico abre "Mis órdenes".
   2. Pasa la orden a `EN_DIAGNOSTICO` y escribe el diagnóstico.
   3. Registra servicios y repuestos.
   4. Si falta un repuesto, pasa la orden a `ESPERANDO_REPUESTOS`.
   5. Al terminar, la pasa a `REPARADO`.
3. **Entrega:** revisar la liquidación y pasar la orden a `ENTREGADO`.
4. **Inventario:** ver la alerta de stock bajo y registrar la entrada de mercancía.
5. **Cliente:** abrir el enlace y ver el estado, la línea de tiempo y la liquidación.

**Pantallas:**
- Inicio de sesión.
- Dashboard.
- Órdenes: lista, detalle y nueva orden (recepción).
- Mis órdenes (vista del mecánico).
- Clientes: lista, detalle y formulario.
- Vehículo: detalle e historial.
- Inventario: lista, repuesto, entrada y ajuste.
- Reportes.
- Administración: usuarios, servicios y datos del taller.
- Seguimiento público.

Los bocetos de cada pantalla están en el **Anexo A**.

**Heurísticas de Nielsen aplicadas:**

| Heurística | Cómo se aplica |
|---|---|
| Visibilidad del estado del sistema | Etiqueta de estado con ícono y texto, línea de tiempo, mensajes de confirmación y marcadores de carga |
| Relación con el mundo real | Vocabulario del taller |
| Control y libertad del usuario | Quitar un repuesto devuelve el stock; se pide confirmación antes de entregar o cancelar |
| Consistencia | Componentes únicos y la acción principal siempre en el mismo lugar |
| Prevención de errores | Solo se ofrecen las transiciones válidas, se muestra el stock disponible y la placa se normaliza |
| Reconocer antes que recordar | Búsqueda de placa con autocompletado y repuestos elegidos de una lista |
| Flexibilidad y eficiencia | Búsqueda global por placa y botón "Nueva orden" siempre visible |
| Diseño minimalista | Una acción principal por pantalla y los campos opcionales plegados |
| Ayuda ante errores | Mensajes concretos, por ejemplo "Solo quedan 2 filtros" |
| Ayuda y aprendizaje | Pantallas vacías que explican qué hacer y una guía rápida (RF-21) |

**Componentes reutilizables:**
- Barra superior con búsqueda de placa.
- Navegación inferior en el celular y lateral en la PC.
- `ChipEstado`.
- `TarjetaOrden`.
- `TablaPaginada`, que en el celular se muestra como tarjetas.
- `CampoFormulario`.
- `BotonPrimario`.
- `Aviso`.
- `DialogoConfirmacion`.
- `EstadoVacio`.
- `Esqueleto`.
- `AlertaStock`.

**Diseño visual:**
- Se prueba en anchos de 360, 768, 1024 y 1440 px.
- Contraste nivel AA.
- Escala de espacios fija.
- Sin degradados ni el estilo genérico de las interfaces generadas automáticamente.

---

## 12. Comandos previstos

Se confirman en la Fase 1.

| Propósito | Backend | Frontend |
|---|---|---|
| Desarrollo | `uvicorn app.main:app --reload` | `npm run dev` |
| Pruebas | `pytest` | — (lista de verificación manual, §15) |
| Revisión de estilo y formato | `ruff check . && ruff format .` | `npm run lint` |
| Migraciones de base de datos | `alembic upgrade head` | — |
| Compilación | — | `npm run build` (el backend sirve la carpeta compilada) |
| Crear un taller y su administrador | script de administración (ADR-006) | — |

---

## 13. Estructura prevista del repositorio

Se crea en la Fase 1. No se crea nada antes de aprobar este SPEC.

```
/
├── SPEC.md
├── docs/
│   ├── decisions/        ADR-001 … ADR-006
│   ├── modelo-datos.md
│   └── modelo-datos.dbml
├── backend/              FastAPI: api/ · schemas/ · services/ · models/ · core/ · tests/
├── frontend/             React + Vite + Tailwind
└── *.md                  documentos de la tesis (D1, D2, D3)
```

---

## 14. Estilo de código

- **Idioma de los nombres:** los términos del dominio van en español y sin tildes (`orden_trabajo`, `registrar_repuesto`), igual que en la tesis. Los términos que imponen los frameworks se dejan en inglés.
- **Python:**
  - estilo PEP 8;
  - `snake_case` para funciones y variables, `PascalCase` para clases;
  - Ruff como revisor de estilo y formateador;
  - tipos en todas las funciones públicas.
- **JavaScript y React:**
  - `camelCase` para variables, `PascalCase` para componentes;
  - un componente por archivo, de menos de 200 líneas;
  - ESLint y Prettier.
- **Base de datos:**
  - tablas y columnas en `snake_case` y en singular;
  - restricciones con nombre explícito, por ejemplo `uq_vehiculo_taller_placa` o `ck_repuesto_stock_no_negativo`.
- **Comentarios:** explican el *por qué*, no el *qué*. No se deja código comentado.
- **Commits:** en español, en imperativo y uno por cambio lógico.

---

## 15. Estrategia de pruebas (un solo desarrollador)

| Nivel | Herramienta | Qué cubre | Exigencia |
|---|---|---|---|
| Reglas de negocio | pytest | Reglas RN-01 a RN-21, transiciones de §7 y cálculo de la liquidación | Obligatorio: al menos una prueba por regla. En el MVP de 4 semanas solo se exigen las reglas críticas (§17.1). |
| API e integración | pytest + cliente HTTP de FastAPI, contra PostgreSQL de prueba (no SQLite) | Autenticación, permisos por rol, aislamiento entre talleres y formato de errores | Obligatorio: cada recurso tiene una prueba que intenta leer datos de otro taller |
| Concurrencia de stock | pytest | Dos registros simultáneos de un repuesto sin stock suficiente | Obligatorio (Fase 4) |
| Interfaz | Lista de verificación manual por pantalla | Los cuatro anchos de pantalla, uso con teclado y estados vacío, de error y de carga | Obligatorio antes de cerrar cada fase |
| Accesibilidad | Lighthouse o axe | Contraste y etiquetas | Fase 7 |
| Pruebas automatizadas de extremo a extremo | — | Fuera de alcance por el tamaño del equipo | — |

---

## 16. Límites de trabajo

**Siempre:**
- Validar la entrada en la API.
- Filtrar por `taller_id`.
- Calcular los totales en el servidor.
- Ejecutar `pytest` antes de cada commit.
- Actualizar el SPEC o el ADR antes de cambiar una decisión.
- Pedir solo los datos personales necesarios.
- Usar **solo datos ficticios** en desarrollo y demostraciones. Los datos reales se usan únicamente en el piloto final y con la autorización correspondiente (H-5).

**Preguntar antes de hacer:**
- Cambiar el modelo de datos aprobado.
- Agregar dependencias que no estén en los ADR.
- Cambiar el alcance o la clasificación MoSCoW.
- Cambiar de proveedor de hosting.
- Crear roles nuevos.
- Activar una función *Could*.

**Nunca:**
- Guardar secretos en el repositorio.
- Guardar tokens en `localStorage`.
- Armar consultas SQL concatenando texto.
- Borrar físicamente órdenes, historial o movimientos.
- Mostrar datos personales en la página pública.
- Usar microservicios o Kubernetes.
- Integrar con la DIAN.

---

## 17. Plan de ejecución

### 17.1 Cronograma operativo vigente: MVP en 4 semanas (H-2)

La sustentación es en diciembre de 2026. El **MVP funcional y demostrable** debe estar listo en 4 semanas, entre el 26/10 y el 22/11/2026.

**Supuesto de dedicación:** unas 35 a 40 horas por semana. Con 20 horas por semana el plazo no alcanza (ver R-13).

**Principios del plan:**
- Se construye por cortes verticales: base de datos, API e interfaz de cada función a la vez.
- Al final de cada semana se hace una demostración.
- Se despliega un esqueleto desde la semana 1 para que el despliegue final no traiga sorpresas.
- Las pruebas automatizadas cubren solo lo crítico.

| Semana | Fechas | Objetivo | Entregables (RF) | Demostración | Criterio de cierre |
|---|---|---|---|---|---|
| **1** | 26/10 – 01/11 | Fundaciones | Proyecto FastAPI, proyecto React y PostgreSQL configurados. Migraciones de `taller` y `usuario`. Script para crear un taller y su administrador. Login y logout (RF-01). Roles (RF-02). Gestión de usuarios (RF-16). Rutas protegidas. Diseño base adaptable al celular (RF-17). **Punto de control de React el miércoles 28/10** (ADR-004). Esqueleto desplegado (recomendado). | El usuario inicia sesión y entra al sistema | Pruebas de login correcto y fallido, respuestas 401 y 403, y un usuario que no puede ver datos de otro taller |
| **2** | 02/11 – 08/11 | Gestión básica | Clientes con autorización de datos (RF-03). Vehículos (RF-04). Formularios, búsqueda por placa y CRUD. | Registrar un cliente y un vehículo, y consultarlos | Placa duplicada responde 422. No se guarda un cliente sin autorización. Prueba de aislamiento entre talleres. |
| **3** | 09/11 – 15/11 | Núcleo del negocio | Recepción y órdenes (RF-05). Estados de §7 con historial (RF-06). Asignación de mecánicos y "Mis órdenes" (RF-07). Historial del vehículo (RF-11). | Crear una orden y moverla entre estados | Transiciones probadas: válidas, inválidas y sin retorno desde ESPERANDO_REPUESTOS. Reglas RN-08, RN-13 y RN-17 probadas. |
| **4** | 16/11 – 22/11 | Completar el MVP | Inventario: catálogo, entradas y ajustes (RF-08). Repuestos en la orden con descuento de stock (RF-09). Alertas (RF-10). Liquidación (RF-12). Seguimiento público (RF-13). Dashboard mínimo (RF-14). Despliegue básico. | Flujo completo: cliente → vehículo → orden → asignación → estados → inventario → liquidación → seguimiento del cliente | El stock nunca queda negativo. El seguimiento no muestra datos personales. URL pública con HTTPS. Datos ficticios cargados. |

**Simplificaciones aceptadas para cumplir el plazo.** El modelo de datos aprobado no cambia.

- **Pruebas automatizadas en el MVP**, solo para:
  - autenticación y roles;
  - aislamiento entre talleres;
  - transiciones de estado;
  - stock;
  - liquidación.

  El resto se verifica con la lista de verificación manual. RNF-09 se completa después del MVP.
- **RF-14 (dashboard):** en el MVP solo muestra conteos por estado y alertas de stock. El dashboard completo se hace después.
- **RF-15 (reportes):** se implementan **después** del MVP, según la instrucción del autor de aplazar los reportes complejos. Los datos que necesita el reporte R2 se registran desde la semana 3 en `historial_estado_orden`, así que no se pierde evidencia.
- **Mano de obra sin catálogo:** se escribe como texto libre. El modelo ya lo admite, porque `orden_servicio.servicio_id` puede ser nulo. RF-18 queda aplazado.
- **Paginación:** solo botones de anterior y siguiente.
- **Diseño visual:** se usan los componentes base de §11. El pulido visual se hace después del MVP.

**Lo que no se simplifica.** Esta seguridad mínima va desde la semana 1:
- hash argon2id de las contraseñas;
- cookie httpOnly;
- filtro por `taller_id`;
- validación de la entrada;
- consultas parametrizadas.

**Si una semana se atrasa, recortar en este orden:**
1. RF-14 mínimo pasa a después del MVP.
2. El rol RECEPCION se oculta de la interfaz y el ADMIN hace sus tareas. El rol sigue en el modelo.
3. Los ajustes de inventario pasan a después del MVP. Las entradas no se recortan.
4. El despliegue pasa a la semana 5 y la demostración se hace en local.

**Nunca se recortan:**
- RF-06, RF-09, RF-12 y RF-13, que forman el flujo completo;
- el aislamiento entre talleres;
- la seguridad mínima.

**Funciones aplazables si falta tiempo:** RF-18 a RF-26.

### 17.2 Después del MVP (desde el 23/11/2026 hasta la sustentación en diciembre)

La fecha exacta de sustentación no está confirmada.

| Bloque | Contenido |
|---|---|
| Semana 5 | Reportes RF-15, con prioridad en R2 porque es la evidencia de la tesis. Dashboard completo. Seguridad: límite de solicitudes, cabeceras y auditoría de dependencias. Completar RNF-09. Anonimización del cliente (RN-11, RNF-06; decisión S2-5). |
| Semana 6 | Manual (RF-21). Funciones *Should* si hay tiempo. Preparar los instrumentos del piloto. |
| Semana 7 en adelante | Piloto con datos reales y autorización (H-5): medir primero el proceso en papel, capacitar y aplicar el cuestionario de usabilidad. Ajustar los capítulos de la tesis (H-3). |

### 17.3 Cronograma de referencia de 20,5 semanas (archivado)

Este era el plan original, con unas 20 horas por semana. Se conserva solo como referencia ideal y **ya no es el cronograma operativo** (H-2).

| Fase | Contenido | Semanas | Semana acumulada | Hito / criterio de cierre |
|---|---|---|---|---|
| F0 | Especificación y ADR (este paquete) | — | S0 | SPEC y ADR aprobados |
| F1 | Fundamentos: proyectos, base de datos, migraciones, `taller` y `usuario`, script de administración, inicio y cierre de sesión, roles, diseño base | 2,5 | S2,5 | **Punto de control de React** en la semana 2 (ADR-004). Inicio de sesión y respuestas 401/403 con pruebas. |
| F2 | Clientes, vehículos y gestión de usuarios (RF-03, RF-04, RF-16) | 2 | S4,5 | Placa duplicada responde 422; aislamiento entre talleres probado |
| F3 | Órdenes, estados, asignaciones y "Mis órdenes" (RF-05, RF-06, RF-07) | 2,5 | S7 | Todas las transiciones de §7 probadas |
| F4 | Inventario y repuestos en la orden (RF-08, RF-09, RF-10) | 2,5 | S9,5 | El stock nunca queda negativo, incluso con operaciones simultáneas |
| F5 | Liquidación, historial, seguimiento, WhatsApp y catálogo de servicios (RF-11, RF-12, RF-13, RF-18, RF-19, RF-20) | 2 | S11,5 | **MVP completo de extremo a extremo**; la página pública no muestra datos personales |
| F6 | Dashboard y reportes R1 a R4 (RF-14, RF-15) | 1,5 | S13 | R2 verificado con datos de prueba |
| F7 | Calidad y seguridad: revisión del código, límite de solicitudes, cabeceras de seguridad, auditoría de dependencias y accesibilidad | 1,5 | S14,5 | Ningún hallazgo crítico |
| F8 | Despliegue gratuito, datos de demostración y manual de usuario (RF-21) | 1 | S15,5 | URL pública con HTTPS y respaldo de la base probado |
| F9 | Piloto: medir el proceso en papel, capacitar, usar el sistema y aplicar el cuestionario de usabilidad | 3 | S18,5 | Datos de al menos 3 talleres (2 formales y 1 informal) |
| — | Reserva para imprevistos (~12 %) | 2 | **S20,5** | — |

**Orden de trabajo:**
- F1 a F5 son estrictamente secuenciales.
- El manual (F8) se puede escribir durante F6 y F7.
- Los instrumentos del piloto (F9) se pueden preparar durante F6.

**Qué recortar si el plazo es menor, en este orden:**
1. Todas las funciones *Could* (ya están fuera del plan).
2. RF-19.
3. RF-18 (en su lugar, la línea de mano de obra se escribe como texto libre).
4. El rol `RECEPCION` (sus tareas las hace el ADMIN).
5. RF-20.
6. La Fase 7, reducida a lo mínimo de seguridad.

**Nunca se recortan** RF-06, RF-13 y RF-15, porque producen la evidencia de la tesis.

---

## 18. Riesgos

P/I = probabilidad / impacto.

| ID | Riesgo | P/I | Mitigación |
|---|---|---|---|
| R-01 | **Académico:** D1 y D3 describen como hechos un piloto y una capacitación que aún no se han hecho con este software | Alta/Alta | Reescribir los capítulos 4 y 7 con los datos del piloto (§17.2, H-3) |
| R-02 | No hay una medición del proceso actual (en papel) para comparar | Alta/Alta | En la Fase 9, cronometrar el proceso en papel antes de usar el sistema |
| R-03 | Un solo desarrollador: enfermedad, carga académica o bloqueos | Alta/Alta | Reserva de 2 semanas, lista de recortes y fases cortas con punto de control |
| R-04 | Curva de aprendizaje de React | Media/Alta | Punto de control el miércoles 28/10 y plan B con Jinja documentado en ADR-004 |
| R-05 | Datos de un taller visibles para otro | Media/Alta | ADR-006 y pruebas de aislamiento obligatorias |
| R-06 | Stock inconsistente por operaciones simultáneas | Baja/Media | Bloqueo de la fila durante la transacción y restricción CHECK |
| R-07 | Plan gratuito: arranque lento tras inactividad, límites de almacenamiento o vencimiento | Alta/Media | Abrir el sistema antes de cada sesión del piloto y no cronometrar ese arranque; respaldo semanal; tener identificado un segundo proveedor |
| R-08 | Rechazo de los talleres informales | Media/Alta | Diseño para el celular, pocos campos y capacitación presencial |
| R-09 | Conexión a internet débil en el taller | Media/Media | Pantallas livianas; la limitación queda documentada |
| R-10 | Crecimiento del alcance (DIAN, citas, notificaciones) | Alta/Media | Respetar la clasificación MoSCoW; todo cambio pasa por el SPEC |
| R-11 | Uso de datos personales reales sin una política de tratamiento del taller | Media/Alta | RN-10, RN-11 y HTTPS; decidir H-5 |
| R-12 | Un piloto en 10 talleres no es viable para una sola persona | Alta/Media | Mínimo 3 talleres; los demás son opcionales (H-3) |
| R-13 | **Plazo de 4 semanas para un solo desarrollador.** El alcance de las semanas 1 a 4 equivale a unas 140-160 horas. | Alta/Alta | Dedicación de 35 a 40 h por semana. Simplificaciones y orden de recortes de §17.1. Demostración semanal para detectar atrasos a tiempo. Esqueleto desplegado en la semana 1. |

---

## 19. Criterios de éxito

### 19.1 MVP de 4 semanas (22/11/2026)

1. El flujo completo (cliente → vehículo → orden → asignación → estados → inventario → liquidación → seguimiento) funciona en la URL pública con HTTPS desde un celular de 360 px.
2. RF-01 a RF-14 funcionan, con RF-14 en su versión mínima.
3. Las pruebas críticas de §17.1 pasan.
4. Solo hay datos ficticios cargados.

### 19.2 Versión para la sustentación

1. Todos los requisitos *Must* (RF-01 a RF-17) funcionan en la URL pública con HTTPS.
2. `pytest` pasa por completo y cubre RN-01 a RN-21, las transiciones de §7 y el aislamiento entre talleres.
3. Una orden recorre el ciclo completo, de `RECIBIDO` a `ENTREGADO`, desde un celular de 360 px, y el cliente la ve en su enlace.
4. El reporte R2 calcula los tiempos por etapa con datos reales del piloto.
5. La revisión de seguridad de la Fase 7 no deja hallazgos críticos.
6. El piloto produce datos de tiempo y de usabilidad en al menos 3 talleres.
7. La infraestructura cuesta $0.

---

## 20. Verificación de consistencia entre documentos

✓ = consistente · ⚠ = requiere una acción del autor.

| Elemento | Investigación (D1-D3) | Requisitos | Arquitectura | Modelo de datos | ADR | Resultado |
|---|---|---|---|---|---|---|
| Arquitectura cliente-servidor | D1 §2.2.1; D3 | RNF-10 | §8 | — | 001 | ✓ |
| Base de datos relacional | D1 glosario | RNF-09 | §8 | 12 tablas | 003 | ✓ |
| Roles administrador, mecánico y cliente | D1 glosario (RBAC) | RF-02 | Capa de servicios | `usuario.rol`; el cliente no tiene cuenta | 005 | ✓ (el cliente accede por enlace, P-4) |
| Estados de la orden | D1 Tabla 2 y D3 hablan de **4 estados** | RF-06 define 6 | — | `estado_orden` | — | ⚠ La tesis debe actualizarse (H-3) |
| Repuestos vinculados a la orden | D1 Tabla 2 | RF-09 | — | `orden_repuesto` y `movimiento_inventario` | — | ✓ |
| Alertas de stock | D1 Tabla 2; D3 | RF-10 | — | `stock_minimo` | — | ✓ |
| Almacenamiento en la nube | D1 Tabla 2; D3 | RNF-11 | §8 (despliegue) | — | 001, 003 | ✓ (planes gratuitos, P-6) |
| Historial accesible al cliente | D3 | RF-13, RF-19 | — | consulta, sin tabla propia | 005 | ✓ (solo la titularidad actual, RN-21) |
| Transparencia de precios | D1 §1.3; D2; D3 | RF-12 | — | líneas con copia del precio | — | ✓ |
| Notificaciones al cliente | D1 §1.3 | RF-20 (envío manual) | — | — | — | ✓ (la limitación está declarada) |
| Asignación de técnicos | D1 Cap. 1 | RF-07 | — | `mecanico_id` y `asignacion_orden` | — | ✓ |
| Medición de tiempos de respuesta | D1 §1.1 (pregunta), §7.3 | RF-15 (R2) | — | `historial_estado_orden` | — | ✓ |
| Ley 1581 | D1 §3.6 | RF-03, RNF-06 | — | `autoriza_datos` y anonimización | 005 | ✓ (datos ficticios hasta el piloto, H-5) |
| Usabilidad en talleres informales | D1 Tabla 2; D2 | RF-17, RNF-01, RNF-08 | — | — | 004 | ✓ |
| Equipo de desarrollo | El consentimiento de D1 nombra **3 investigadores** | P-1: **un desarrollador** | — | — | — | ⚠ Aclarar en la tesis (H-3) |
| Talleres del piloto | D1 §3.3.4 habla de los talleres participantes (10) | Criterio de éxito 6: mínimo 3 | — | — | — | ⚠ Se corrige más adelante en la tesis (H-3) |
| Agendamiento de citas | D1 §3.2.3 | RF-26 (Could) | — | sin modelo | — | ✓ (aplazado explícitamente) |

---

## 21. Registro de decisiones

### 21.1 Decisiones cerradas (23/10/2026)

| ID | Decisión |
|---|---|
| P-1 | Un solo desarrollador, con nivel básico a intermedio en Python, JavaScript y bases de datos |
| P-2 | Una sola instalación para varios talleres, con aislamiento lógico por `taller_id` |
| P-3 | El sistema se desarrolla desde cero; los documentos de la tesis son antecedentes |
| P-4 | El cliente no tiene cuenta; accede con un enlace único por orden |
| P-5 | Se agrega el estado `ESPERANDO_REPUESTOS` y existe el estado `CANCELADA` |
| P-6 | Sin presupuesto: hosting gratuito y portable |
| P-7 | Cada mecánico tiene su propio usuario y toda su actividad queda registrada |
| P-9 | Liquidación sin IVA y sin integración con la DIAN |

### 21.2 Decisiones de cierre de la Fase 0 (23/10/2026)

| ID | Decisión del autor |
|---|---|
| H-1 | `ESPERANDO_REPUESTOS` es opcional. No se puede volver de `ESPERANDO_REPUESTOS` a `EN_DIAGNOSTICO` (§7). |
| H-2 | La sustentación es en diciembre. El MVP debe estar listo en 4 semanas (§17.1). El cronograma de 20,5 semanas queda archivado como referencia (§17.3). |
| H-3 | Las inconsistencias de la tesis se corrigen más adelante y no bloquean el desarrollo. Se mantienen solo como referencia (Anexo B). |
| H-4 | El cliente solo ve las órdenes de su titularidad actual, nunca las de propietarios anteriores (RN-21). |
| H-5 | Se usan datos ficticios en desarrollo y demostraciones. Los datos reales se usan solo en el piloto final, con la autorización correspondiente (§16). |

### 21.3 Estado de la Fase 0

**APROBADA el 23/10/2026.** El autor aprobó este SPEC, el modelo de datos, los ADR-001 a ADR-006 y la arquitectura.

La Fase 1 (semana 1 de §17.1) **solo empieza con la autorización expresa del autor**.

### 21.4 Decisiones de la Semana 2 (aprobadas por el autor el 25/10/2026)

| ID | Decisión |
|---|---|
| S2-1 | La placa, ya normalizada (RN-20), tiene de 5 a 7 letras o números. |
| S2-2 | El teléfono tiene de 7 a 15 dígitos, con un `+` inicial opcional. Se guarda sin espacios, guiones, puntos ni paréntesis. |
| S2-3 | El documento se guarda sin espacios, puntos ni guiones y es único por taller cuando se registra. Un documento repetido responde 422, igual que una placa repetida. |
| S2-4 | No se puede asociar un vehículo, ni al crearlo ni al cambiarle el dueño, a un cliente desactivado. |
| S2-5 | La anonimización del cliente (RN-11, RNF-06) se aplaza hasta después del MVP funcional (§17.2). |

---

## Anexo A — Bocetos de pantallas

**Inicio de sesión**
```
┌──────────────────────────────┐
│   [logo]  Taller Digital      │
│  Correo   [________________]  │
│  Clave    [__________] [👁]   │
│  [      Ingresar       ]      │
│  ⚠ Correo o clave incorrectos │  ← mensaje genérico
└──────────────────────────────┘
```

**Dashboard**
```
┌ Buscar placa [ABC123 🔍]                              [+ Nueva orden] ┐
│ Recibidos 3 │ Diagnóstico 5 │ Esperando rep. 2 │ Reparados 2 │ Entregados hoy 4 │
│ ⚠ Stock bajo (3): Filtro aceite W712 – quedan 2             [Ver]   │
│ #128 ABC123 Mazda 3   [● En diagnóstico]       Juan   →             │
│ #127 XYZ987 Spark     [● Esperando repuestos]  Pedro  →             │
└──────────────────────────────────────────────────────────────────────┘
```

**Clientes**
```
Clientes  [Buscar nombre/teléfono]                [+ Cliente]
┌ Ana Gómez · 300 123 4567 · 2 carros                      → ┐
Formulario: Nombre* · Teléfono* · Correo · Documento
[☐] Autorizo el tratamiento de mis datos (Ley 1581)*
[Cancelar]                                         [Guardar]
```

**Vehículo e historial**
```
ABC123 · Mazda 3 2015 · Rojo        Dueño: Ana Gómez →
[+ Nueva orden para este carro]
12/03/2026 #098 Cambio de aceite      45.200 km  $180.000 ✓
04/10/2026 #128 Ruido en suspensión   48.900 km  en curso
```

**Orden de trabajo**
```
Orden #128 · ABC123 Mazda 3                    [● En diagnóstico]
Recibido 08:10 ✓ → Diagnóstico 09:02 ● → Esperando rep. → Reparado → Entregado
Mecánico: Juan [reasignar]   Km: 48.900   Motivo: ruido delantero
Diagnóstico: [______________________]   Trabajo realizado: [__________]
Mano de obra [+]  Revisión suspensión    1 × $60.000   (Juan)
Repuestos    [+]  Buje tijera (stock 4)  2 × $35.000   (Juan)
Total: $130.000
[Enviar por WhatsApp]  [Esperando repuestos]  [ Marcar Reparado ▶ ]
```

**Inventario**
```
Inventario [Buscar] [⚠ Stock bajo]          [+ Entrada] [Ajuste]
W712  Filtro aceite   2 ⚠  mín 5   $25.000
B330  Buje tijera     4    mín 2   $35.000
Movimientos: SALIDA −2 · Orden #128 · Juan · 09:40
```

**Reportes**
```
Periodo [01/10/2026 – 23/10/2026]   Mecánico [Todos ▾]
R1 Órdenes por estado        R2 Tiempo promedio por etapa
R3 Repuestos más usados      R4 Stock bajo
```

**Seguimiento público**
```
Taller Norte · Orden #128 · Placa ABC***
[● Esperando repuestos]  Actualizado 11:15
Recibido ✓ → Diagnóstico ✓ → Esperando repuestos ● → Reparado → Entregado
Mano de obra $60.000 · Repuestos $70.000 · Total $130.000
```

## Anexo B — Inconsistencias en los documentos de la tesis (no afectan al software)

| ID | Inconsistencia |
|---|---|
| I-1 | D1 §3.4.2 menciona una grabación de audio, pero el consentimiento dice que no habrá grabaciones de voz. |
| I-2 | La primera frase de D1 §3.4.3 dice que hubo encuesta a la Población 1, y el párrafo siguiente lo contradice. |
| I-3 | La modalidad de la entrevista no coincide: D2 dice "virtual" y D1 habla de visitas presenciales. |
| I-4 | Errores de formato: capítulos que saltan del 4 al 7, Ilustración 1 y 2, encabezados de tabla "Column 1" y "Column 6", "Evi dencia", la frase "medidas de" sin completar, la fórmula de la muestra y una frase cortada en el consentimiento. |
| I-5 | Citas: los años de Restrepo, Silberschatz, Pressman, Hernández Sampieri y Ortiz no coinciden entre el texto y las referencias; faltan Tamayo y Sabino en las referencias; la fuente del 9 % no es la misma en todos los lugares. |
| I-6 | La tesis habla de 4 estados de orden; este SPEC define 6 (P-5). |
| I-7 | La tesis menciona 3 investigadores; el desarrollo lo hace una sola persona (P-1). |
