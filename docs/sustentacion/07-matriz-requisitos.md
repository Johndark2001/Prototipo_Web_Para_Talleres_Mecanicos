# Matriz final de requisitos — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Jurados y docentes |
| Corte | 28/10/2026 — commit `84f20f3` |
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

En la evidencia, `test_x` remite a `backend/tests/test_x.py`. «Validación manual» se refiere a las validaciones funcionales del autor al cerrar cada semana (en la Semana 4, una validación de punta a punta con 32 de 32 verificaciones).

---

## 1. Requisitos funcionales (RF)

| Código | Nombre | Prioridad | Semana | Estado | Evidencia | Observaciones |
|---|---|---|---|---|---|---|
| RF-01 | Inicio y cierre de sesión | Must | S1 | **Implementado** | `test_auth` (13 pruebas); pantalla Login; botón Salir | JWT en cookie httpOnly, sesión de 8 h, mensaje genérico ante fallos |
| RF-02 | Roles ADMIN, RECEPCION y MECANICO | Must | S1 | **Implementado** | `test_usuarios`, pruebas de permisos en cada archivo; `api/deps.py` | El rol se relee de la base en cada solicitud |
| RF-03 | Gestión de clientes con búsqueda y autorización de datos | Must | S2 | **Implementado** | `test_clientes` (17); pantallas Clientes, Detalle y Formulario | Búsqueda por nombre, teléfono o documento; autorización obligatoria con fecha |
| RF-04 | Vehículos ligados al cliente, placa única por taller | Must | S2 | **Implementado** | `test_vehiculos` (16); búsqueda global «Buscar placa» | Placa normalizada de 5 a 7 caracteres (S2-1); cambio de dueño |
| RF-05 | Recepción: abrir la orden desde la placa, con motivo y kilometraje | Must | S3 | **Implementado** | `test_ordenes`; pantalla Nueva orden | Incluye la entrega estimada (S3-4) y el mecánico opcional; RNF-02 se medirá en el piloto |
| RF-06 | Estados de la orden con historial (fecha, usuario, nota) | Must | S3 | **Implementado** | `test_flujo_orden` (9), `test_ordenes` (30); línea de tiempo e historial | 6 estados; «Esperando repuestos» opcional (H-1); retroceso solo ADMIN |
| RF-07 | Asignar y reasignar mecánico con historial; «Mis órdenes» | Must | S3 | **Implementado** | `test_ordenes` (reasignación, Mis órdenes, lista de mecánicos) | El mecánico anterior deja de ver la orden (S3-5); carga visible (S3-6) |
| RF-08 | Catálogo de repuestos con stock, mínimo, entradas y ajustes | Must | S4 | **Implementado** | `test_inventario` (19); pantallas Inventario y Repuesto | Ajuste por conteo físico con motivo obligatorio (S4-1); solo ADMIN mueve el stock (S4-4) |
| RF-09 | Repuestos en la orden con descuento automático del stock | Must | S4 | **Implementado** | `test_liquidacion`, `test_concurrencia_stock` | Transacción única; devolución al quitar o cancelar |
| RF-10 | Alertas de stock mínimo en el dashboard y el inventario | Must | S4 | **Implementado** | `test_inventario`, `test_dashboard` | «Stock bajo» y «Agotado» con texto e ícono |
| RF-11 | Historial de mantenimiento por vehículo | Must | S3 | **Implementado** | `test_ordenes` (filtro por vehículo); detalle del carro | Muestra todas las órdenes del carro |
| RF-12 | Liquidación: servicios + repuestos = total, sin IVA | Must | S4 | **Implementado** | `test_liquidacion` (19) | Calculada en el servidor con decimales exactos |
| RF-13 | Seguimiento público con enlace único | Must | S4 | **Implementado** | `test_seguimiento` (5); página `/seguimiento/:codigo` | 128 bits aleatorios, sin datos personales, 30 consultas/min por IP; aún sin URL pública (S4-8) |
| RF-14 | Dashboard: órdenes por estado, órdenes del día, alertas | Must | S4 | **Parcial** | `test_dashboard` (4); pantalla Inicio | Versión mínima aprobada (§17.1). El dashboard completo está pendiente para la Semana 5 |
| RF-15 | Reportes R1 a R4 (R2: tiempo promedio por etapa) | Must | — | **Pendiente** (Semana 5) | Los datos ya se registran en `historial_estado_orden` desde S3 | Aplazado por decisión del autor (§17.1); R2 tiene prioridad porque es la evidencia de la tesis |
| RF-16 | Gestión de usuarios por el ADMIN | Must | S1 | **Implementado** | `test_usuarios` (10); pantalla Usuarios | Crear, cambiar rol, activar y desactivar. **No** incluye cambio ni recuperación de clave |
| RF-17 | Interfaz primero para el celular, con lenguaje del taller | Must | S1–S4 | **Implementado** | Validación manual en 360, 768, 1024 y 1440 px; validación responsive de la anonimización | La auditoría con Lighthouse o axe está pendiente (§15) |
| RF-18 | Catálogo de servicios de mano de obra | Should | — | **Aplazado** | La tabla `servicio` existe vacía y sin API (S4-9) | La mano de obra se escribe como texto libre |
| RF-19 | Historial del vehículo en el enlace del cliente | Should | — | **Aplazado** (S4-7) | — | El enlace muestra solo la orden consultada |
| RF-20 | Botón «Enviar por WhatsApp» | Should | — | **Aplazado** (S4-7) | — | El enlace se copia con «Copiar enlace» |
| RF-21 | Manual de usuario y guía rápida | Should | — | **Pendiente** (Semana 6) | Este paquete incluye el manual de usuario y el del administrador | Falta la guía rápida de una página para el piloto |
| RF-22 | Exportar reportes a CSV | Could | — | **Aplazado** | — | Depende de RF-15 |
| RF-23 | Liquidación imprimible | Could | — | **Aplazado** | — | — |
| RF-24 | Lista de verificación al recibir el carro | Could | — | **Aplazado** | — | Sin modelo de datos |
| RF-25 | Recordatorio de próximo mantenimiento | Could | — | **Aplazado** | — | Sin modelo de datos |
| RF-26 | Agendamiento de citas | Could | — | **Aplazado** | — | Sin modelo de datos |

**Resumen RF:** 15 implementados, 1 parcial, 2 pendientes, 8 aplazados. **De los 17 requisitos Must, 15 están implementados, 1 es parcial (RF-14) y 1 está pendiente (RF-15).**

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
| RNF-07 | Accesibilidad AA, teclado, etiquetas, estado no solo por color | S1–S4 | **Parcial** | Componentes con etiquetas, `aria-*`, texto e ícono en los estados | Falta la auditoría formal con Lighthouse o axe |
| RNF-08 | Lenguaje del taller | S1–S4 | **Implementado** | Textos de la interfaz y mensajes de error en español del taller | — |
| RNF-09 | Al menos una prueba por regla de negocio | S1–S4 | **Parcial** | 214 pruebas; las reglas críticas están cubiertas | Completar y documentar la cobertura en la Semana 5 |
| RNF-10 | Configuración solo por variables de entorno | S1 | **Implementado** | `core/config.py`, `.env.example` | — |
| RNF-11 | $0 de infraestructura | — | **Implementado en local; pendiente en la nube** | — | Depende de los planes gratuitos de Render y Neon |

---

## 4. Funciones fuera de alcance (no se construyen)

Facturación electrónica DIAN e IVA · pagos en línea · cuentas de cliente · notificaciones automáticas (SMS, correo, API de WhatsApp) · funcionamiento sin conexión y app nativa · fotos y adjuntos · proveedores, compras, contabilidad y nómina · varias sedes por taller · MTBF y MTTR · inteligencia artificial · pantalla de superadministración (SPEC §2.2).
