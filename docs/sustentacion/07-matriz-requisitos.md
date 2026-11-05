# Matriz final de requisitos — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Jurados y docentes |
| Corte | 05/11/2026 — commit `e51d187` más los ajustes visuales del 05/11/2026 (SPEC §21.11) |
| Fuente de los requisitos | [SPEC.md](../../SPEC.md) §4 (RF), §5 (RNF), §6 (RN) |

**Estados:** **Implementado** · **Parcial** (versión mínima aprobada) · **Pendiente** (planificado para la Semana 5 o 6) · **Aplazado** (Should/Could sin fecha) · **Fuera de alcance**.

**Semanas y commits:**

| Semana | Commit | Fecha |
|---|---|---|
| S1 — Fundaciones | `a314c7c` | 23/10/2026 |
| S2 — Clientes y vehículos | `e02fcb3` | 25/10/2026 |
| S3 — Órdenes, estados y asignación | `fb3f819` | 25/10/2026 |
| S4 — Inventario, liquidación y seguimiento | `ee5c2f4` | 26/10/2026 |
| Anonimización (posterior al MVP) | `84f20f3` | 28/10/2026 |
| Rediseño y tipo de vehículo (V-1 a V-5) | `e3fc487` | 04/11/2026 |
| Orden vertical, PDF, categoría, cliente con vehículo (O-1 a O-9) | `e51d187` | 04/11/2026 |
| Terminología «Cliente» y fondos (T-1 a T-3) | Sin commit | 05/11/2026 |

En la evidencia, `test_x` remite a `backend/tests/test_x.py`. «Validación manual» se refiere a las validaciones funcionales del autor al cerrar cada semana (en la Semana 4, una validación de punta a punta con 32 de 32 verificaciones).

---

## 1. Requisitos funcionales (RF)

| Código | Nombre | Prioridad | Semana | Estado | Evidencia | Observaciones |
|---|---|---|---|---|---|---|
| RF-01 | Inicio y cierre de sesión | Must | S1 | **Implementado** | `test_auth` (13 pruebas); pantalla Login; botón Salir | JWT en cookie httpOnly, sesión de 8 h, mensaje genérico ante fallos |
| RF-02 | Roles ADMIN, RECEPCION y MECANICO | Must | S1 | **Implementado** | `test_usuarios`, pruebas de permisos en cada archivo; `api/deps.py` | El rol se relee de la base en cada solicitud |
| RF-03 | Gestión de clientes con búsqueda y autorización de datos | Must | S2 | **Implementado** | `test_clientes` (17), `test_cliente_con_vehiculo` (6); pantallas Clientes, Detalle y Formulario | Búsqueda por nombre, teléfono o documento; autorización obligatoria con fecha; alta con el primer vehículo en una transacción (O-8, O-9) |
| RF-04 | Vehículos ligados al cliente, placa única por taller | Must | S2 | **Implementado** | `test_vehiculos` (24 funciones, 35 casos); búsqueda global «Buscar placa»; filtro Todos/Carros/Motos | Placa normalizada de 5 a 7 caracteres (S2-1); cambio de cliente; tipo CARRO o MOTO combinable con la placa (V-1 a V-3) |
| RF-05 | Recepción: abrir la orden desde la placa, con motivo y kilometraje | Must | S3 | **Implementado** | `test_ordenes`, `test_categoria_problema` (14); pantalla Nueva orden | El motivo se registra como categoría del catálogo (22 carro, 20 moto) más la observación del cliente (O-5 a O-7). Incluye la entrega estimada (S3-4) y el mecánico opcional; RNF-02 se medirá en el piloto |
| RF-06 | Estados de la orden con historial (fecha, usuario, nota) | Must | S3 | **Implementado** | `test_flujo_orden` (9), `test_ordenes` (30); línea de tiempo e historial | 6 estados; «Esperando repuestos» opcional (H-1); retroceso solo ADMIN. Vista de la orden en una columna (O-1) |
| RF-07 | Asignar y reasignar mecánico con historial; «Mis órdenes» | Must | S3 | **Implementado** | `test_ordenes` (reasignación, Mis órdenes, lista de mecánicos) | El mecánico anterior deja de ver la orden (S3-5); carga visible (S3-6) |
| RF-08 | Catálogo de repuestos con stock, mínimo, entradas y ajustes | Must | S4 | **Implementado** | `test_inventario` (19); pantallas Inventario y Repuesto | Ajuste por conteo físico con motivo obligatorio (S4-1); solo ADMIN mueve el stock (S4-4) |
| RF-09 | Repuestos en la orden con descuento automático del stock | Must | S4 | **Implementado** | `test_liquidacion`, `test_concurrencia_stock` | Transacción única; devolución al quitar o cancelar |
| RF-10 | Alertas de stock mínimo en el dashboard y el inventario | Must | S4 | **Implementado** | `test_inventario`, `test_dashboard` | «Stock bajo» y «Agotado» con texto e ícono |
| RF-11 | Historial de mantenimiento por vehículo | Must | S3 | **Implementado** | `test_ordenes` (filtro por vehículo); detalle del carro | Muestra todas las órdenes del carro |
| RF-12 | Liquidación: servicios + repuestos = total, sin IVA | Must | S4 | **Implementado** | `test_liquidacion` (19) | Calculada en el servidor con decimales exactos |
| RF-13 | Seguimiento público con enlace único | Must | S4 | **Implementado** | `test_seguimiento` (5), `test_informe_pdf`; página `/seguimiento/:codigo` | 128 bits aleatorios, sin datos personales, 30 consultas/min por IP; aún sin URL pública (S4-8). Descarga del informe PDF al entregar (O-3) |
| RF-14 | Dashboard: órdenes por estado, órdenes del día, alertas | Must | S4 | **Parcial** | `test_dashboard` (4); pantalla Inicio | Versión mínima aprobada (§17.1). El dashboard completo está pendiente para la Semana 5 |
| RF-15 | Reportes R1 a R4 (R2: tiempo promedio por etapa) | Must | — | **Pendiente** (Semana 5) | Los datos ya se registran en `historial_estado_orden` desde S3 | Aplazado por decisión del autor (§17.1); R2 tiene prioridad porque es la evidencia de la tesis |
| RF-16 | Gestión de usuarios por el ADMIN | Must | S1 | **Implementado** | `test_usuarios` (10); pantalla Usuarios | Crear, cambiar rol, activar y desactivar. **No** incluye cambio ni recuperación de clave |
| RF-17 | Interfaz primero para el celular, con lenguaje del taller | Must | S1–S4 | **Implementado** | Validación manual en 360, 768, 1024 y 1440 px; validación responsive de la anonimización; capturas de las 6 vistas de módulo en 390 y 1440 px (05/11/2026) | Rediseño (V-4), terminología «Cliente» (T-1) y fondos por módulo (T-2). La auditoría con Lighthouse o axe está pendiente (§15) |
| RF-18 | Catálogo de servicios de mano de obra | Should | — | **Aplazado** | La tabla `servicio` existe vacía y sin API (S4-9) | La mano de obra se escribe como texto libre |
| RF-19 | Historial del vehículo en el enlace del cliente | Should | — | **Aplazado** (S4-7) | — | El enlace muestra solo la orden consultada |
| RF-20 | Botón «Enviar por WhatsApp» | Should | — | **Aplazado** (S4-7) | — | El enlace se copia con «Copiar enlace» |
| RF-21 | Manual de usuario y guía rápida | Should | — | **Pendiente** (Semana 6) | Este paquete incluye el manual de usuario y el del administrador | Falta la guía rápida de una página para el piloto |
| RF-22 | Exportar reportes a CSV | Could | — | **Aplazado** | — | Depende de RF-15 |
| RF-23 | Liquidación imprimible | Could | 04/11 | **Parcial** | `test_informe_pdf` (12 funciones, 16 casos); botón «Descargar informe PDF» | El informe final en PDF incluye la liquidación, pero **solo existe para órdenes entregadas** (O-2). La liquidación de una orden abierta no se imprime |
| RF-24 | Lista de verificación al recibir el carro | Could | — | **Aplazado** | — | Sin modelo de datos |
| RF-25 | Recordatorio de próximo mantenimiento | Could | — | **Aplazado** | — | Sin modelo de datos |
| RF-26 | Agendamiento de citas | Could | — | **Aplazado** | — | Sin modelo de datos |

**Resumen RF:** 15 implementados, 2 parciales (RF-14 y RF-23), 2 pendientes, 7 aplazados. **De los 17 requisitos Must, 15 están implementados, 1 es parcial (RF-14) y 1 está pendiente (RF-15).**

---

## 2. Reglas de negocio (RN)

| Código | Nombre | Semana | Estado | Evidencia | Observaciones |
|---|---|---|---|---|---|
| RN-01 | Cambios de estado solo por transiciones válidas, con historial | S3 | **Implementado** | `test_flujo_orden`, `test_ordenes` | Estado anterior, nuevo, usuario, fecha y nota |
| RN-02 | Descuento de stock en una transacción; nunca negativo | S4 | **Implementado** | `test_inventario`, `test_liquidacion`, `test_concurrencia_stock` | CHECK en la base + bloqueo de fila |
| RN-03 | Quitar repuesto o cancelar devuelve el stock | S4 | **Implementado** | `test_liquidacion` | Movimiento `DEVOLUCION` (S4-2) |
| RN-04 | Alerta cuando el stock ≤ mínimo | S4 | **Implementado** | `test_inventario`, `test_dashboard` | — |
| RN-05 | Precio copiado en cada línea | S4 | **Implementado** | `test_liquidacion` | Cambiar el catálogo no altera órdenes existentes |
| RN-06 | Liquidación calculada en el servidor, sin total guardado ni IVA | S4 | **Implementado** | `test_liquidacion` | — |
| RN-07 | Orden entregada o cancelada no se modifica | S3–S4 | **Implementado** | `test_ordenes` (`test_rn07…`), `test_flujo_orden`, `test_liquidacion` | Aplica a los datos, los estados y las líneas |
| RN-08 | Máximo una orden abierta por vehículo | S3 | **Implementado** | `test_ordenes`, `test_concurrencia_ordenes` | Índice único parcial; probado con recepciones simultáneas |
| RN-09 | Todo se limita al taller del usuario; otro taller = «no encontrado» | S1–S4 | **Implementado** | Pruebas de aislamiento en todos los archivos de recursos | ADR-006 |
| RN-10 | Sin autorización de datos no se registra el cliente | S2 | **Implementado** | `test_clientes` (API y CHECK de la base) | — |
| RN-11 | No se borra la historia; desactivar; anonimizar datos personales | S2 (desactivar), 28/10 (anonimizar) | **Implementado** | `test_anonimizacion` (15), pruebas de desactivación en cada recurso | Decisiones A-1 a A-7 (SPEC §21.7) |
| RN-12 | Consecutivo por taller; código de seguimiento de ≥128 bits | S3 | **Implementado** | `test_ordenes`, `test_concurrencia_ordenes` | Bloqueo de la fila del taller |
| RN-13 | Para iniciar diagnóstico debe haber mecánico | S3 | **Implementado** | `test_ordenes` (`test_rn13…`) | La interfaz también lo advierte |
| RN-14 | Cada asignación queda registrada | S3 | **Implementado** | `test_ordenes` (`test_reasignar_registra_cada_asignacion`) | — |
| RN-15 | Cada línea y cada movimiento registran su usuario | S4 | **Implementado** | `test_liquidacion`, `test_inventario` | — |
| RN-16 | El mecánico solo trabaja sus órdenes; no se desactiva con órdenes abiertas | S3 | **Implementado** | `test_ordenes` (`test_rn16…`, Mis órdenes) | También impide cambiarle el rol (S3-2) |
| RN-17 | Para pasar a Reparado, el trabajo realizado no puede estar vacío | S3 | **Implementado** | `test_ordenes` (`test_rn17…`) | — |
| RN-18 | Cancelar exige motivo | S3 | **Implementado** | `test_ordenes`, `test_flujo_orden` | CHECK en la base |
| RN-19 | Cantidades decimales y montos exactos | S4 | **Implementado** | `test_liquidacion`, `test_inventario` | `NUMERIC`, nunca coma flotante |
| RN-20 | Placa normalizada | S2 | **Implementado** | `test_vehiculos` | Mayúsculas, sin espacios ni guiones |
| RN-21 | El enlace público solo muestra la titularidad actual | S4 | **Implementado por diseño** | `test_seguimiento` | Como RF-19 está aplazado, el enlace muestra **únicamente** la orden consultada; la regla se cumple de forma trivial |

**Resumen RN:** 21 de 21 implementadas.

---

## 3. Requisitos no funcionales (RNF)

| Código | Nombre | Semana | Estado | Evidencia | Observaciones |
|---|---|---|---|---|---|
| RNF-01 | Uso en celular desde 360 px | S1–S4 | **Implementado** | Validación manual por pantalla | — |
| RNF-02 | Abrir una orden en ≤ 3 pasos y < 2 min | S3 | **Implementado (diseño); medición pendiente** | Flujo «Nueva orden para este carro» | Se mide en el piloto |
| RNF-03 | Listados < 2 s con 5.000 órdenes por taller | — | **Pendiente de medición** | Paginación (máx. 100), índices | Prueba de carga no realizada |
| RNF-04 | argon2id, HTTPS, cookie httpOnly, permisos por solicitud | S1 | **Parcial** | `test_auth` | Falta HTTPS (despliegue, Semana 5) |
| RNF-05 | Aislamiento entre talleres probado por recurso | S1–S4 | **Implementado** | Pruebas de aislamiento en cada archivo | — |
| RNF-06 | Ley 1581: autorización con fecha, datos mínimos y anonimización | S2 + 28/10 | **Implementado** | `test_clientes`, `test_anonimizacion` | Decisiones A-1 a A-7 |
| RNF-07 | Accesibilidad AA, teclado, etiquetas, estado no solo por color | S1–S4 | **Parcial** | Componentes con etiquetas, `aria-*`, texto e ícono en los estados y en el tipo de vehículo | Falta la auditoría formal con Lighthouse o axe. **Limitación conocida (T-3):** con los fondos al 50 %, un texto gris justo sobre una línea del dibujo baja a ~3:1; tarjetas, listas y formularios no se ven afectados |
| RNF-08 | Lenguaje del taller | S1–S4 | **Implementado** | Textos de la interfaz y mensajes de error en español del taller | — |
| RNF-09 | Al menos una prueba por regla de negocio | S1–S4 | **Parcial** | 263 pruebas (200 funciones, 16 archivos); cobertura del backend 91 % (97 % sin los scripts de consola), medida el 05/11/2026 | Las 21 reglas tienen evidencia en la sección 2. Falta formalizar la trazabilidad regla → prueba y fijar la medición de cobertura en el proyecto (Semana 5) |
| RNF-10 | Configuración solo por variables de entorno | S1 | **Implementado** | `core/config.py`, `.env.example` | — |
| RNF-11 | $0 de infraestructura | — | **Implementado en local; pendiente en la nube** | — | Depende de los planes gratuitos de Render y Neon |

---

## 4. Decisiones posteriores al MVP (SPEC §21.9 a §21.11)

| Decisión | Qué cambia | Requisitos | Estado | Evidencia |
|---|---|---|---|---|
| V-1 a V-3 | Tipo de vehículo CARRO o MOTO, filtro en el API y en la lista | RF-04, RNF-07 | **Implementado y aprobado** (04/11) | `test_vehiculos` (10 pruebas nuevas), migración 0006 |
| V-4, V-5 | Rediseño visual sin dependencias nuevas | RF-17 | **Implementado y aprobado** (04/11) | Validación manual del autor |
| O-1 | Vista de la orden en una columna | RF-06 | **Implementado y aprobado** (04/11) | Validación manual del autor |
| O-2 a O-4 | Informe PDF final (interno y público) con fpdf2 | RF-13, RF-23 | **Implementado y aprobado** (04/11) | `test_informe_pdf` |
| O-5 a O-7 | Categoría del problema y observación del cliente | RF-05 | **Implementado y aprobado** (04/11) | `test_categoria_problema`, migración 0007 |
| O-8, O-9 | Alta de cliente con vehículo | RF-03, RF-04 | **Implementado y aprobado** (04/11) | `test_cliente_con_vehiculo` |
| T-1 | «Cliente» en lugar de «Dueño» en la interfaz | RNF-08 | **Implementado** (05/11), pendiente de commit | Búsqueda en el código: no queda «Dueño» visible; 263 pruebas pasan |
| T-2, T-3 | Fondos temáticos por módulo al 50 % | RF-17, RNF-07 | **Implementado** (05/11), pendiente de commit | Capturas de 14 vistas; opacidad medida 0,5 |

---

## 5. Funciones fuera de alcance (no se construyen)

Facturación electrónica DIAN e IVA · pagos en línea · cuentas de cliente · notificaciones automáticas (SMS, correo, API de WhatsApp) · funcionamiento sin conexión y app nativa · fotos y adjuntos · proveedores, compras, contabilidad y nómina · varias sedes por taller · MTBF y MTTR · inteligencia artificial · pantalla de superadministración (SPEC §2.2).
