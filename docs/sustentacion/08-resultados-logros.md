# Resultados y logros del proyecto — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Jurados y docentes |
| Corte | 28/10/2026 — commit `84f20f3` |

Este documento presenta los resultados **del desarrollo del software**: qué funciona, cómo se verificó y qué problemas se resolvieron. **No** incluye resultados de un piloto en talleres reales, porque todavía no se ha realizado (ver [Trabajo futuro](09-trabajo-futuro.md)).

---

## 1. Resultados en cifras

| Indicador | Valor |
|---|---|
| Requisitos funcionales *Must* implementados | 15 de 17 completos, 1 parcial (RF-14), 1 pendiente (RF-15) |
| Reglas de negocio implementadas | 21 de 21 |
| Pruebas automatizadas | **214** (180 funciones de prueba, 13 archivos), **todas pasan** |
| Pruebas de concurrencia | 3 (consecutivo de órdenes, orden abierta única, stock) |
| Operaciones de la API | 35 |
| Pantallas de la interfaz | 17 (incluidas el inicio de sesión, la página pública de seguimiento y la de página no encontrada) |
| Tablas de la base de datos | 12, con 5 migraciones versionadas |
| Decisiones de arquitectura documentadas | 6 ADR |
| Decisiones de diseño registradas en el SPEC | 41 (8 P, 5 H, 5 S2, 7 S3, 9 S4 y 7 A) |
| Validación de punta a punta de la Semana 4 | 32 de 32 verificaciones correctas |
| Costo de infraestructura hasta hoy | $0 (entorno local) |
| Datos personales reales usados | Ninguno (solo datos ficticios, H-5) |

---

## 2. Módulos que funcionan

Todos estos módulos funcionan en el entorno local, con datos ficticios, y el autor los validó.

| Módulo | Qué se puede hacer hoy | Validado en |
|---|---|---|
| **Acceso** | Iniciar y cerrar sesión; sesión de 8 h; acceso cortado al instante si el usuario es desactivado | Semana 1 |
| **Usuarios** | Crear, cambiar rol, desactivar y activar; protección contra quitarse el propio acceso | Semana 1 |
| **Diseño adaptable** | Menú inferior en el celular y lateral en el PC; búsqueda global por placa | Semanas 1 a 4 |
| **Clientes** | Registrar con autorización de datos, buscar, editar, desactivar | Semana 2 |
| **Vehículos** | Registrar con placa normalizada, cambiar dueño, desactivar, ver el historial | Semanas 2 y 3 |
| **Órdenes** | Abrir desde la placa, consecutivo por taller, 6 estados, notas, cancelación, retroceso | Semana 3 |
| **Asignación** | Asignar y reasignar con historial; «Mis órdenes» del mecánico; carga por mecánico | Semana 3 |
| **Inventario** | Catálogo, entradas, ajustes por conteo, movimientos, alertas | Semana 4 |
| **Líneas de la orden** | Mano de obra en texto libre; repuestos con descuento y devolución automática | Semana 4 |
| **Liquidación** | Mano de obra + repuestos = total, sin IVA, calculado en el servidor | Semana 4 |
| **Seguimiento público** | Enlace por orden, sin cuenta, sin datos personales, con límite de consultas | Semana 4 |
| **Inicio (dashboard mínimo)** | Conteos por estado, entregados hoy, alertas de stock; «Mis órdenes abiertas» para el mecánico | Semana 4 |
| **Anonimización** | Borrar los datos personales del cliente conservando la historia, con auditoría | 28/10/2026 |
| **Varios talleres** | Dos talleres en la misma base sin ver los datos del otro | Semanas 1 a 4 |

---

## 3. Validaciones realizadas

### 3.1 Validación funcional del autor al cierre de cada semana

| Semana | Demostración (SPEC §17.1) | Criterio de cierre verificado |
|---|---|---|
| 1 | El usuario inicia sesión y entra al sistema | Login correcto y fallido, 401 y 403, un usuario no ve datos de otro taller |
| 2 | Registrar un cliente y un vehículo y consultarlos | Placa duplicada → 422; no se guarda un cliente sin autorización; aislamiento |
| 3 | Crear una orden y moverla entre estados | Transiciones válidas e inválidas, sin retorno desde «Esperando repuestos»; RN-08, RN-13, RN-17 |
| 4 | Flujo completo: cliente → vehículo → orden → asignación → estados → inventario → liquidación → seguimiento | Stock nunca negativo; el seguimiento no muestra datos personales; datos ficticios cargados. **32 de 32 verificaciones correctas** |

### 3.2 Validación funcional de la anonimización (28/10/2026)

El autor verificó manualmente:

1. Anonimización de clientes.
2. Confirmación obligatoria con la palabra ANONIMIZAR.
3. Restricción por roles (solo el administrador).
4. Conservación de órdenes e historial.
5. Conservación de los vehículos asociados.
6. Seguimiento público funcionando después de anonimizar.
7. Bloqueo de la anonimización con órdenes abiertas.
8. Bloqueo de la edición y la reactivación de clientes anonimizados.
9. Reutilización del documento para un cliente nuevo.
10. Visualización correcta del cliente anonimizado en todas las pantallas.
11. Validación en celular (responsive).

### 3.3 Revisión manual de la interfaz

Por cada pantalla se revisaron:
- los anchos de 360, 768, 1024 y 1440 px;
- el uso con teclado;
- los estados vacío, de error y de carga.

Las pruebas automatizadas de extremo a extremo de la interfaz quedaron **fuera de alcance** por el tamaño del equipo (SPEC §15).

### 3.4 Calidad estática

- **Ruff** (Python): revisión de estilo y formato sin hallazgos.
- **ESLint** (JavaScript): sin hallazgos.
- **`npm run build`**: la interfaz compila sin errores.

---

## 4. Pruebas automatizadas

Las pruebas corren con **pytest contra PostgreSQL real** (no SQLite). Antes de cada ejecución se aplican **todas las migraciones desde cero**, así que también se prueban las migraciones. La base de pruebas se vacía después de cada prueba.

| Archivo | Funciones de prueba | Qué demuestra |
|---|---|---|
| `test_auth.py` | 13 | Login con cookie segura, mismo mensaje para correo inexistente y clave incorrecta, hash argon2id, rechazo de un token alterado, corte inmediato al desactivar, rechazo de modificaciones sin JSON (CSRF) |
| `test_usuarios.py` | 10 | Solo el ADMIN gestiona usuarios; correo único; clave mínima; aislamiento; nadie se quita su propio acceso |
| `test_clientes.py` | 17+ | Autorización obligatoria (API y restricción de la base); normalización de teléfono, correo y documento; documento único por taller; búsqueda; permisos |
| `test_vehiculos.py` | 16+ | Placa normalizada y única por taller; cambio de dueño; no asociar clientes inactivos |
| `test_flujo_orden.py` | 9+ | Matriz de transiciones por rol; sin retorno desde «Esperando repuestos» (H-1) |
| `test_ordenes.py` | 30+ | Recepción, consecutivo, RN-08, RN-13, RN-16, RN-17, RN-18, RN-07, reasignación, «Mis órdenes» |
| `test_concurrencia_ordenes.py` | 2 | Dos recepciones simultáneas reciben números distintos; dos recepciones del mismo carro abren una sola orden |
| `test_inventario.py` | 19+ | Catálogo, entradas, ajustes, alertas, permisos |
| `test_concurrencia_stock.py` | 1 | Registros simultáneos de un repuesto nunca dejan el stock negativo |
| `test_liquidacion.py` | 19+ | Cálculo exacto, precio congelado, devolución al quitar o cancelar, órdenes cerradas |
| `test_dashboard.py` | 4 | Conteos, alertas ordenadas por urgencia, aislamiento, rol |
| `test_seguimiento.py` | 5+ | Acceso sin sesión, ningún dato personal ni interno en la respuesta, 404 con código inválido, 429 al superar el límite |
| `test_anonimizacion.py` | 15+ | Datos borrados, auditoría, conservación de la historia, seguimiento funcionando, solo ADMIN, confirmación escrita, A-1, irreversibilidad, aislamiento, CHECK de la base |
| **Total** | **180 funciones → 214 ejecuciones** | |

(«+» indica que el archivo tiene pruebas parametrizadas, que se ejecutan varias veces con datos distintos. Por eso las 180 funciones dan 214 ejecuciones.)

**Evolución:** 25 pruebas en la Semana 1 → 194 al cerrar la Semana 4 (63 nuevas en esa semana) → 214 con la anonimización.

---

## 5. Problemas encontrados y cómo se resolvieron

| N.º | Problema | Cuándo | Causa | Solución |
|---|---|---|---|---|
| 1 | **Error 500** al guardar un vehículo con el año o el color vacíos | Semana 2 | Un campo vacío del formulario llegaba como texto vacío y no como nulo | Validador que convierte los textos vacíos en nulo (`vacio_a_nulo`), corregido en el mismo commit `e02fcb3` |
| 2 | **Riesgo de números de orden repetidos** con dos recepciones al mismo tiempo | Semana 3 | El consecutivo se calcula leyendo y escribiendo el siguiente número | Bloqueo de la fila del taller (`SELECT … FOR UPDATE`) + restricción única `(taller_id, numero)`; prueba de concurrencia |
| 3 | **Riesgo de dos órdenes abiertas para el mismo carro** | Semana 3 | Dos recepciones simultáneas del mismo carro | Índice único parcial en la base (`uq_orden_vehiculo_abierta`); el error se traduce a «El carro … ya tiene una orden abierta», con enlace a esa orden |
| 4 | **Riesgo de stock negativo** con dos registros simultáneos | Semana 4 | Condición de carrera entre leer y descontar el stock | Bloqueo de la fila del repuesto, `CHECK stock_actual >= 0` y transacción única; prueba de concurrencia |
| 5 | **`FOR UPDATE` incompatible con cargas de relaciones opcionales** | Semanas 3–4 | PostgreSQL no permite bloquear el lado nulo de un `LEFT OUTER JOIN` | Las consultas con bloqueo no usan `joinedload` sobre relaciones que pueden ser nulas (por ejemplo, el mecánico) |
| 6 | **Riesgo de mostrar fechas un día antes** | Semana 3 | Convertir «2026-11-10» con `Date` en el navegador aplica la zona UTC−5 de Colombia | La fecha estimada se formatea como texto, sin convertirla a fecha y hora (`formatearDia`) |
| 7 | **Revelar qué correos están registrados** por la diferencia de tiempo del login | Semana 1 | Verificar una clave con argon2 tarda; si el correo no existe, la respuesta sería más rápida | Se verifica contra un hash ficticio para igualar el tiempo, y el mensaje es siempre «Correo o clave incorrectos» |
| 8 | **CSRF** con la sesión en una cookie | Semana 1 | El navegador envía la cookie automáticamente | `SameSite=Lax` y un middleware que exige JSON en toda modificación (415 si no lo es) |
| 9 | **Fecha de auditoría de la anonimización en otra zona horaria** que la del resto de fechas | 28/10 | La hora se tomaba del reloj de la aplicación en UTC | Se usa la hora de la base (`now()`), igual que en las demás fechas; detectado por una prueba automatizada |
| 10 | **Cliente anonimizado sin teléfono** mostraba enlaces de llamada vacíos | 28/10 | Las pantallas asumían que siempre hay teléfono | Las pantallas omiten el teléfono cuando está vacío |
| 11 | **Datos personales en el enlace público** | Semana 4 | Riesgo de exponer datos por agregar campos sin querer | Esquema de salida con **lista blanca** de campos y una prueba que busca nombre, teléfono, placa completa, motivo, kilometraje y usuarios en la respuesta |
| 12 | **Despliegue no disponible** al cerrar el MVP | Semana 4 | Requiere crear cuentas en Render y Neon | Decisión S4-8: el despliegue pasa a la Semana 5 y el MVP se valida en local, como prevé el recorte 4 del plan |
| 13 | **Scripts de npm bloqueados en Windows** | Entorno | La política de ejecución de PowerShell impedía correr `npm` | Se ajustó la política de ejecución del usuario. No afecta al código |

---

## 6. Logros destacables

1. **Flujo operativo completo y trazable**, de la recepción a la entrega, con el cliente informado por enlace.
2. **Integridad garantizada en dos niveles**: las reglas críticas se validan en el servicio **y** en la base de datos (CHECK, índices únicos parciales, FK `RESTRICT`).
3. **Concurrencia probada**, algo poco común en prototipos académicos.
4. **Privacidad desde el diseño**: autorización obligatoria, enlace público sin datos personales y anonimización auditada que conserva la historia.
5. **Aislamiento entre talleres** probado en cada recurso.
6. **Especificación antes del código** (SPEC y ADR) y **trazabilidad** de cada requisito a la tesis.
7. **Instrumento de investigación listo**: el historial de estados ya guarda las marcas de tiempo que necesita el reporte R2 para responder la pregunta de investigación.

---

## 7. Lo que estos resultados no demuestran todavía

| Aspecto | Por qué no está demostrado | Cómo se demostrará |
|---|---|---|
| Reducción de los tiempos de atención | No hay piloto ni línea base del proceso en papel | Medir primero en papel y luego con el sistema (Semana 7 en adelante) |
| Usabilidad para talleres informales | No hay usuarios reales todavía | Cuestionario de usabilidad en el piloto |
| Rendimiento con 5.000 órdenes por taller (RNF-03) | No se hizo una prueba de carga | Prueba con datos sintéticos después del despliegue |
| Funcionamiento en la nube y con HTTPS | El despliegue está pendiente | Semana 5 |
