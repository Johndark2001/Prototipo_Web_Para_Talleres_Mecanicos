# Manual del administrador — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Dueño, administrador o gerente del taller (rol `ADMIN`) |
| Versión del sistema | Commit `84f20f3` (28/10/2026) |
| Complementa | [Manual de usuario](01-manual-usuario.md), con el paso a paso de cada pantalla |

El administrador hace todo lo que hace Recepción y, además, gestiona los usuarios, el catálogo y el stock del inventario, puede devolver una orden al estado anterior y es el único que puede anonimizar a un cliente.

---

## 1. Roles del sistema

El sistema tiene **tres roles** para el personal del taller. El cliente final **no tiene cuenta**: entra con un enlace por orden (decisión P-4).

| Rol | En la pantalla | Perfil típico | Dispositivo principal | Para qué existe |
|---|---|---|---|---|
| `ADMIN` | Administrador | Dueño, administrador o gerente | PC y celular | Ver todo el taller, gestionar personas e inventario y tomar las decisiones delicadas |
| `RECEPCION` | Recepción | Recepcionista o asesor de servicio | PC | Recibir carros, asignar mecánicos, informar al cliente y entregar |
| `MECANICO` | Mecánico | Cada mecánico, con su propio usuario (P-7) | Celular | Ver sus órdenes, diagnosticar, registrar el trabajo y los repuestos, y avanzar el estado |

**Taller sin recepcionista.** El administrador hace también las tareas de recepción; no hace falta crear un usuario de Recepción.

**Cada persona, su usuario.** No comparta usuarios. El historial dice quién abrió cada orden, quién la cambió de estado, quién registró cada repuesto y quién movió el inventario. Si dos personas usan el mismo usuario, esa trazabilidad se pierde.

---

## 2. Permisos de cada rol

Esta matriz es la del SPEC §3. Se verifica **en el servidor en cada solicitud**: aunque alguien modifique la página en su navegador, el servidor rechaza la acción con «Su rol no tiene permiso para esta acción».

| Acción | Administrador | Recepción | Mecánico |
|---|---|---|---|
| Gestionar los usuarios del taller | Sí | — | — |
| Crear y editar clientes y vehículos | Sí | Sí | Solo ver |
| Anonimizar un cliente | Sí | — | — |
| Abrir una orden y asignar o reasignar mecánico | Sí | Sí | — |
| Ver órdenes | Todas | Todas | Solo las asignadas a él |
| Registrar diagnóstico, trabajo, mano de obra y repuestos | Sí | Sí | Solo en sus órdenes |
| Iniciar diagnóstico, esperando repuestos, marcar reparado | Sí | — | Sí, en sus órdenes |
| Entregar y cancelar | Sí | Sí | — |
| Devolver una orden al estado anterior (con nota) | Sí | — | — |
| Catálogo de repuestos, entradas y ajustes | Sí | — | — |
| Consultar la lista del inventario | Sí | Sí | Sí |
| Detalle y movimientos de un repuesto | Sí | — | — |
| Resumen del taller (Inicio) | Sí | Sí | Vista «Mis órdenes abiertas» |
| Copiar el enlace de seguimiento | Sí | Sí | — |

**Reglas que cruzan los roles:**
- Al **reasignar** una orden, el mecánico anterior deja de verla (S3-5).
- El mecánico **solo** cambia el diagnóstico y el trabajo realizado de la recepción; no puede corregir el motivo de ingreso, el kilometraje ni la fecha estimada.
- Todas las acciones se limitan al **taller del usuario**. Ningún rol ve datos de otro taller.

---

## 3. Alta y baja de usuarios

### 3.1 Alta (crear un usuario)

1. Menú **Usuarios** → **+ Usuario**.
2. Escriba **Nombre**, **Correo**, **Clave inicial** (mínimo 8 caracteres) y **Rol**.
3. **Guardar usuario**.
4. Entregue el correo y la clave a la persona **en privado**, nunca por un grupo de chat.

Tenga en cuenta:
- El correo es **único en todo el sistema**, no solo en su taller, porque al iniciar sesión no se elige el taller.
- La clave se guarda con **hash argon2id**. Nadie, ni siquiera el desarrollador, puede ver la clave original.
- En esta versión **no hay pantalla para cambiar ni recuperar la clave** (pendiente). Si una persona olvida su clave, la alternativa vigente es crearle un usuario nuevo con otro correo y desactivar el anterior.

### 3.2 Cambio de rol

En la lista, cambie el valor de **Rol de [nombre]**. El cambio aplica de inmediato.

**Restricciones:**
- No puede cambiar **su propio** rol (para evitar que un taller se quede sin administrador por error).
- No puede cambiarle el rol a un **mecánico con órdenes abiertas**; primero reasigne sus órdenes (S3-2).
- No se cambia el rol de un usuario inactivo; primero actívelo.

### 3.3 Baja (desactivar un usuario)

1. En la fila de la persona, toque **Desactivar**.
2. Confirme: «[nombre] perderá el acceso de inmediato. Su historial se conserva.»

Qué pasa:
- La persona **pierde el acceso al instante**, aunque tenga una sesión abierta, porque el sistema relee al usuario en cada solicitud.
- **No se borra**: su nombre sigue en las órdenes, los historiales y los movimientos (RN-11).
- Se puede **Activar** de nuevo.

**Restricciones:**
- No puede desactivarse a sí mismo.
- No puede desactivar a un **mecánico con órdenes abiertas** (RN-16). El sistema muestra cuántas tiene. Reasígnelas desde cada orden (**Reasignar**) y vuelva a intentar.

### 3.4 Procedimiento recomendado cuando un mecánico se retira

1. En **Órdenes**, revise las órdenes abiertas de ese mecánico.
2. Reasigne cada una a otro mecánico, con el motivo «Retiro de [nombre]».
3. En **Usuarios**, desactive al mecánico.

---

## 4. Gestión de talleres

**Estado: implementada solo por script (decisión de alcance del SPEC §2.2 y ADR-006).** No hay una pantalla para crear o editar talleres.

### 4.1 Cómo se crea un taller

Un taller nuevo y su **primer administrador** los crea el desarrollador o la persona técnica responsable del servidor, con este comando (en la carpeta `backend/`):

```
uv run python -m app.scripts.crear_taller --taller "Nombre del taller" --nombre "Nombre Admin" --email admin@correo.co
```

- La clave del administrador se pide por teclado y no queda en el historial de la terminal.
- La opción `--formal` marca el taller como formal (con registro mercantil).
- Desde ese momento, ese administrador crea a los demás usuarios desde la pantalla **Usuarios**.

### 4.2 Varios talleres en una sola instalación

- Una sola instalación atiende a **varios talleres** con sus datos **separados** (multi-tenant, ADR-006).
- Cada taller tiene su propia numeración de órdenes (#1, #2…), su propio catálogo de repuestos y sus propias placas. Dos talleres pueden tener un carro con la misma placa o un repuesto con el mismo código.
- Si un usuario intenta abrir un recurso de otro taller, el sistema responde «no encontrado», igual que si no existiera.

### 4.3 Lo que no existe todavía

| Función | Estado |
|---|---|
| Pantalla para editar el nombre, teléfono o dirección del taller | Trabajo futuro |
| Pantalla de superadministración para crear talleres | Fuera de alcance (SPEC §2.2) |
| Desactivar un taller completo | Existe el dato `taller.activo` (si está inactivo, nadie de ese taller puede ingresar), pero no hay pantalla; se haría directamente en la base de datos |
| Varias sedes por taller | Fuera de alcance |

---

## 5. Inventario

El administrador es el **único** que mueve el stock y edita el catálogo (S4-4). Recepción y los mecánicos consultan la lista.

### 5.1 Cómo se mueve el stock

| Movimiento | Lo origina | Efecto en el stock | ¿Nota? |
|---|---|---|---|
| `ENTRADA` | El administrador registra mercancía, o crea el repuesto con stock inicial | Suma | Opcional (proveedor o factura) |
| `SALIDA` | Alguien agrega el repuesto a una orden | Resta | Va ligado a la orden |
| `DEVOLUCION` | Se quita el repuesto de una orden abierta o se cancela la orden | Suma | Va ligado a la orden |
| `AJUSTE` | El administrador registra un conteo físico | Deja el stock igual a lo contado | **Obligatoria** |

Cada movimiento guarda el usuario, la fecha, la cantidad con signo y el **stock resultante**. Los movimientos **nunca se borran**.

### 5.2 Garantías del sistema

- **El stock nunca queda negativo** (RN-02). Si no alcanza, la operación se rechaza con «No hay suficiente [repuesto]: quedan …». Lo garantizan el bloqueo de la fila durante la operación y una restricción de la base de datos, y se probó con dos registros simultáneos.
- **El precio queda congelado en la orden** (RN-05): cambiar el precio en el catálogo no altera órdenes ya registradas.
- **Alerta de stock bajo** (RN-04, RF-10): cuando el stock queda igual o por debajo del mínimo, el repuesto aparece en Inicio («N repuestos necesitan reposición») y en el inventario con «Stock bajo» o «Agotado».
- Las cantidades admiten **decimales** (litros, metros) y los precios se guardan como decimales exactos (RN-19).

### 5.3 Rutina sugerida

| Frecuencia | Tarea |
|---|---|
| Diaria | Revisar las alertas de stock en Inicio. |
| Al recibir mercancía | **Registrar entrada** con el número de factura en la nota. |
| Mensual | Conteo físico de los repuestos más usados y **Ajustar por conteo** de los que no cuadren, con el motivo. |
| Cuando un repuesto deja de venderse | **Desactivar** (conserva el historial y el stock). |

---

## 6. Auditoría (trazabilidad)

El sistema no tiene una pantalla de auditoría general. La trazabilidad está **dentro de cada registro** y se consulta en su pantalla.

| Qué se registra | Dónde se guarda | Dónde se ve |
|---|---|---|
| Quién abrió la orden y cuándo | `orden_trabajo.creado_por`, `fecha_ingreso` | Detalle de la orden: «Recibido [fecha] por [nombre]» |
| Cada cambio de estado: estado anterior, nuevo, usuario, fecha y nota (RN-01) | `historial_estado_orden` | Detalle de la orden → **Historial** |
| Cada asignación o reasignación de mecánico, con nota (RN-14) | `asignacion_orden` | Detalle de la orden → **Historial** («Asignó a…», «Reasignó a…») |
| Quién registró cada línea de mano de obra o repuesto (RN-15) | `orden_servicio.registrado_por`, `orden_repuesto.registrado_por` | Detalle de la orden, en cada línea |
| Cada movimiento de inventario, con usuario y stock resultante (RN-15) | `movimiento_inventario` | Detalle del repuesto (solo administrador) |
| Fecha de la autorización de datos del cliente (RN-10) | `cliente.fecha_autorizacion` | Detalle del cliente |
| Quién anonimizó a un cliente y cuándo (A-7) | `cliente.anonimizado_por`, `anonimizado_en` | Detalle del cliente: «Datos personales anonimizados el … por …» |
| Último ingreso de cada usuario | `usuario.ultimo_acceso` | No se muestra en pantalla |

**Garantías:**
- Las órdenes, el historial de estados, las asignaciones y los movimientos **nunca se borran** (RN-11). Las relaciones en la base de datos usan `ON DELETE RESTRICT`, y el código no ejecuta borrados sobre esas tablas.
- Una orden **Entregada** o **Cancelada** ya no se puede modificar (RN-07).
- **Lo que se borra de verdad:** una línea de mano de obra o de repuesto que se **quita** de una orden **abierta** desaparece de la orden. En el caso de un repuesto, la devolución queda en los movimientos de inventario.

**Pendiente:** registro de intentos de inicio de sesión fallidos y reportes de actividad por usuario.

---

## 7. Anonimización

### 7.1 Qué es y por qué existe

La Ley 1581 de 2012 da al titular el derecho a pedir que se supriman sus datos. Pero el taller necesita conservar su historia operativa: órdenes, cobros, inventario y tiempos de cada etapa. La anonimización resuelve las dos cosas: **borra los datos personales y conserva la historia** (RN-11, RNF-06).

### 7.2 Qué hace exactamente

| Dato | Antes | Después |
|---|---|---|
| Nombre | «Ana Gómez» | «Cliente anonimizado N.º [id]» |
| Teléfono | «3001234567» | vacío |
| Correo | «ana@correo.co» | vacío |
| Documento | «1144000111» | vacío (el documento queda libre para un registro nuevo) |
| Estado | Activo | **Inactivo**, sin posibilidad de reactivarlo ni editarlo |
| Autorización y su fecha | Se conservan | Se conservan, como prueba de que el dato se trató con permiso (A-3) |
| Carros (placa, marca, modelo) | — | Se conservan, ligados al mismo cliente (A-5) |
| Órdenes, historial, liquidaciones | — | Se conservan; se ven con el nombre anonimizado |
| Enlace de seguimiento | — | Sigue funcionando; nunca mostró datos personales |
| Auditoría | — | Se registra **quién** (el administrador) y **cuándo** |

### 7.3 Condiciones

| Condición | Motivo | Decisión |
|---|---|---|
| Solo el administrador | Es irreversible | SPEC §3 |
| Hay que escribir **ANONIMIZAR** | Confirmación explícita contra errores | RN-11 |
| El cliente no puede tener órdenes abiertas | El taller necesita contactarlo mientras tenga el carro | A-1 |
| No se puede hacer dos veces | La auditoría original no se reemplaza | A-4 |
| Es irreversible | Si se pudiera deshacer, los datos no estarían borrados | A-4 |

Además de estas reglas de la aplicación, una restricción de la base de datos (`ck_cliente_anonimizacion_coherente`) impide que exista un cliente marcado como anonimizado sin quién y cuándo, con correo o documento, o activo.

### 7.4 Procedimiento recomendado

1. Reciba la solicitud del cliente y **confirme su identidad**.
2. Busque al cliente y revise sus órdenes. Si tiene alguna abierta, entréguela o cancélela.
3. Ejecute la anonimización (Manual de usuario, sección 13).
4. Guarde fuera del sistema la constancia de la solicitud: fecha, medio y respuesta dada. El sistema registra cuándo se hizo, pero no la solicitud del titular.

### 7.5 Lo que la anonimización no cubre (limitaciones conocidas)

- **Textos libres de las órdenes** (motivo de ingreso, diagnóstico, trabajo realizado, notas de estado y de asignación) **no se modifican** (A-6). Si alguien escribió allí datos personales, quedan.
- **La placa** no se anonimiza, porque es un dato del vehículo (A-5).
- **Copias de seguridad:** en el despliegue (pendiente) habrá que definir cuánto tiempo se conservan las copias de seguridad que tengan datos anteriores a la anonimización.

---

## 8. Buenas prácticas

**Personas y accesos**
- Un usuario por persona. Nunca compartir claves.
- Desactivar el mismo día a quien deja el taller.
- Mantener al menos **dos administradores** si el taller lo permite, porque nadie puede quitarse a sí mismo el rol ni el acceso.
- Cerrar sesión (**Salir**) en equipos compartidos.

**Datos personales (Ley 1581)**
- Leer la autorización al cliente antes de marcar la casilla.
- Pedir solo teléfono y nombre; correo y documento solo si el cliente quiere darlos.
- No escribir datos personales en los campos de texto libre de las órdenes, ni en la mano de obra, que el cliente ve en su enlace (S4-6).
- Enviar el enlace de seguimiento solo al dueño del carro.
- Usar **Desactivar** para lo cotidiano y **Anonimizar** solo ante una solicitud del titular.

**Operación**
- Abrir la orden apenas llega el carro: así los tiempos de cada etapa son reales.
- Pedir a los mecánicos que cambien el estado en el momento en que ocurre, no al final del día.
- Escribir notas claras al cancelar, al devolver y al esperar repuestos.
- Registrar las entradas de mercancía el mismo día y hacer conteos físicos periódicos.

**Datos de prueba**
- Mientras no haya piloto, usar **solo datos ficticios** (decisión H-5). La semilla de demostración marca a los clientes con «(demo)».

---

## 9. Restricciones del sistema

### 9.1 Reglas que el sistema hace cumplir

| Regla | Qué impide |
|---|---|
| RN-07 | Modificar una orden entregada o cancelada |
| RN-08 | Abrir una segunda orden para un carro con orden abierta |
| RN-10 | Registrar un cliente sin autorización de datos |
| RN-11 | Borrar órdenes, historial, asignaciones o movimientos |
| RN-13 | Iniciar el diagnóstico sin mecánico asignado |
| RN-16 | Desactivar o cambiar el rol de un mecánico con órdenes abiertas |
| RN-17 | Marcar reparado sin el trabajo realizado |
| RN-18 | Cancelar sin motivo |
| RN-02 | Dejar el stock negativo |
| H-1 | Devolver de «Esperando repuestos» a «En diagnóstico» |
| S2-4 / S3-3 | Asociar carros nuevos o abrir órdenes con clientes o carros inactivos |
| S3-4 | Una entrega estimada anterior a hoy |
| A-1 / A-4 | Anonimizar con órdenes abiertas, dos veces, o deshacerlo |

### 9.2 Limitaciones de esta versión

| Limitación | Estado |
|---|---|
| No hay URL pública ni HTTPS: el sistema funciona en el entorno local | Pendiente (Semana 5: Render + Neon) |
| No hay reportes (tiempos por etapa, repuestos más usados, órdenes por mecánico) | Pendiente (RF-15, Semana 5) |
| El dashboard es mínimo: conteos por estado, entregados hoy y alertas | Parcial (RF-14) |
| No hay cambio ni recuperación de clave | Pendiente |
| No hay límite de intentos de inicio de sesión | Pendiente (seguridad, Semana 5) |
| No hay catálogo de servicios; la mano de obra se escribe como texto libre | Aplazado (RF-18) |
| No hay botón de WhatsApp; el enlace se copia a mano | Aplazado (RF-20) |
| El enlace del cliente muestra solo esa orden, no el historial del carro | Aplazado (RF-19) |
| No hay factura electrónica, IVA ni pagos en línea | Fuera de alcance |
| No funciona sin conexión; no hay app nativa | Fuera de alcance |
| No hay fotos ni archivos adjuntos | Fuera de alcance |
| El plan gratuito previsto puede tardar varios segundos en la primera solicitud tras un rato inactivo | Riesgo R-07, aplica al desplegar |
