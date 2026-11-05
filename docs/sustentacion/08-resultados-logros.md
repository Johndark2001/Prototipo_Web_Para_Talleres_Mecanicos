# Resultados y logros del proyecto — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | Jurados y docentes |
| Corte | 05/11/2026 — commit `e51d187` más los ajustes visuales del 05/11/2026 (SPEC §21.11) |

Este documento presenta los resultados **del desarrollo del software**: qué funciona, cómo se verificó y qué problemas se resolvieron. **No** incluye resultados de un piloto en talleres reales, porque todavía no se ha realizado (ver [Trabajo futuro](09-trabajo-futuro.md)).

---

## 1. Resultados en cifras

| Indicador | Valor |
|---|---|
| Requisitos funcionales *Must* implementados | 15 de 17 completos, 1 parcial (RF-14), 1 pendiente (RF-15) |
| Reglas de negocio implementadas | 21 de 21 |
| Pruebas automatizadas | **263** (200 funciones de prueba, 16 archivos), **todas pasan** |
| Cobertura del backend | **91 %** de 2.144 sentencias (97 % sin los dos scripts de consola) |
| Pruebas de concurrencia | 3 (consecutivo de órdenes, orden abierta única, stock) |
| Operaciones de la API | 38 |
| Pantallas de la interfaz | 17 (incluidas el inicio de sesión, la página pública de seguimiento y la de página no encontrada) |
| Tablas de la base de datos | 12, con 7 migraciones versionadas |
| Categorías del problema | 22 para carro y 20 para moto |
| Decisiones de arquitectura documentadas | 6 ADR |
| Decisiones de diseño registradas en el SPEC | 58 (8 P, 5 H, 5 S2, 7 S3, 9 S4, 7 A, 5 V, 9 O y 3 T) |
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
| **Diseño adaptable** | Menú inferior en el celular y lateral en el PC; búsqueda global por placa; rediseño visual y fondos temáticos por módulo | Semanas 1 a 4; 04/11 y 05/11 |
| **Clientes** | Registrar con autorización de datos y con su primer vehículo en un solo paso, buscar, editar, desactivar | Semana 2; 04/11 |
| **Vehículos** | Carros y motos; registrar con placa normalizada, cambiar el cliente, filtrar por tipo y placa, desactivar, ver el historial | Semanas 2 y 3; 04/11 |
| **Órdenes** | Abrir desde la placa con categoría del problema y observación del cliente, consecutivo por taller, 6 estados, notas, cancelación, retroceso, vista en una columna | Semana 3; 04/11 |
| **Informe PDF** | Descargar el informe final de una orden entregada, desde el taller y desde el enlace del cliente | 04/11/2026 |
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

### 3.3 Validación funcional de los cambios del 04/11/2026

El autor validó en local el rediseño y el tipo de vehículo (V-1 a V-5) y los cambios O-1 a O-9:

1. Informe PDF interno y público de una orden entregada.
2. Alta de cliente con vehículo.
3. Categorías por tipo de vehículo, búsqueda sin tildes y «Otro».
4. Observación del cliente.
5. Vista de la orden en una columna.

### 3.4 Verificación de los ajustes del 05/11/2026

- **Terminología (T-1):** búsqueda en el código de todo «Dueño» visible; quedan solo comentarios internos. Las 263 pruebas pasan tras cambiar el mensaje del backend.
- **Fondos (T-2, T-3):** capturas automáticas con sesión de demostración de 14 vistas (las 6 de módulo en 1440 px y en 390 px, el detalle de una orden y el formulario de vehículo nuevo). Sin desplazamiento horizontal; opacidad medida en el navegador; tarjetas, listas y formularios legibles.

### 3.5 Revisión manual de la interfaz

Por cada pantalla se revisaron:
- los anchos de 360, 768, 1024 y 1440 px;
- el uso con teclado;
- los estados vacío, de error y de carga.

Las pruebas automatizadas de extremo a extremo de la interfaz quedaron **fuera de alcance** por el tamaño del equipo (SPEC §15).

### 3.6 Calidad estática

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
| `test_cliente_con_vehiculo.py` | 6 | Cliente y vehículo se guardan juntos; sin vehículo sigue funcionando; con placa repetida no se guarda nada; el error indica el campo; el mecánico no registra clientes |
| `test_vehiculos.py` | 24+ | Placa normalizada y única por taller; cambio de cliente; no asociar clientes inactivos; tipo por defecto, moto, tipo inválido, filtro por tipo combinado y aislado |
| `test_flujo_orden.py` | 9+ | Matriz de transiciones por rol; sin retorno desde «Esperando repuestos» (H-1) |
| `test_ordenes.py` | 30+ | Recepción, consecutivo, RN-08, RN-13, RN-16, RN-17, RN-18, RN-07, reasignación, «Mis órdenes» |
| `test_categoria_problema.py` | 14+ | Catálogo por tipo terminado en «Otro»; búsqueda sin tildes; la categoría debe ser del tipo; «Otro» exige descripción; forma anterior con `motivo_ingreso`; corrección y órdenes antiguas; el mecánico no la cambia |
| `test_informe_pdf.py` | 12+ | Informe interno completo; admin y mecánico asignado lo descargan, otro mecánico no; sin sesión no hay informe interno; 409 antes de entregar y en canceladas; el público sin datos personales; cliente anonimizado; textos fuera de Latin-1 |
| `test_concurrencia_ordenes.py` | 2 | Dos recepciones simultáneas reciben números distintos; dos recepciones del mismo carro abren una sola orden |
| `test_inventario.py` | 19+ | Catálogo, entradas, ajustes, alertas, permisos |
| `test_concurrencia_stock.py` | 1 | Registros simultáneos de un repuesto nunca dejan el stock negativo |
| `test_liquidacion.py` | 19+ | Cálculo exacto, precio congelado, devolución al quitar o cancelar, órdenes cerradas |
| `test_dashboard.py` | 4 | Conteos, alertas ordenadas por urgencia, aislamiento, rol |
| `test_seguimiento.py` | 5+ | Acceso sin sesión, ningún dato personal ni interno en la respuesta, 404 con código inválido, 429 al superar el límite |
| `test_anonimizacion.py` | 15+ | Datos borrados, auditoría, conservación de la historia, seguimiento funcionando, solo ADMIN, confirmación escrita, A-1, irreversibilidad, aislamiento, CHECK de la base |
| **Total** | **200 funciones → 263 ejecuciones** | |

(«+» indica que el archivo tiene pruebas parametrizadas, que se ejecutan varias veces con datos distintos. Por eso las 200 funciones dan 263 ejecuciones.)

**Evolución:** 25 pruebas en la Semana 1 → 194 al cerrar la Semana 4 (63 nuevas en esa semana) → 214 con la anonimización → 224 con el tipo de vehículo → 263 con el informe PDF, la categoría del problema y el alta de cliente con vehículo.

**Cobertura** (medida el 05/11/2026 con `pytest-cov`): 91 % del backend; 97 % sin contar `crear_taller` y `semilla_demo`, que son scripts de consola sin pruebas. El informe PDF, el catálogo de categorías, la máquina de estados y la liquidación están al 100 %.

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
| 14 | **«No se crea el vehículo»** al registrar un cliente con vehículo | 04/11 | Seguía corriendo un proceso de uvicorn anterior al cambio, que no conocía el campo `vehiculo` | Reiniciar el backend. El código era correcto: lo demostraban las pruebas. La interfaz ahora avisa si el servidor guardó el cliente sin el vehículo |
| 15 | **Textos que el PDF no puede dibujar** (emoji, comillas tipográficas) | 04/11 | La fuente base del PDF solo admite Latin-1 | Se reemplazan antes de escribir el PDF; prueba `test_textos_fuera_de_latin1_no_rompen_el_pdf` |
| 16 | **Órdenes anteriores sin categoría** al introducir el catálogo | 04/11 | El dato no existía antes de la migración 0007 | La migración copia el motivo a la observación; la pantalla y el PDF muestran «Sin categoría» y se pueden corregir (O-6) |
| 17 | **Fondo decorativo frente a contraste** | 05/11 | A mayor opacidad, más se nota la identidad visual, pero baja el contraste del texto que quede encima | Capa detrás del contenido, tarjetas opacas y máscara que deja limpia la zona de títulos; el riesgo residual al 50 % queda documentado (T-3) |

---

## 6. Logros destacables

1. **Flujo operativo completo y trazable**, de la recepción a la entrega, con el cliente informado por enlace.
2. **Integridad garantizada en dos niveles**: las reglas críticas se validan en el servicio **y** en la base de datos (CHECK, índices únicos parciales, FK `RESTRICT`).
3. **Concurrencia probada**, algo poco común en prototipos académicos.
4. **Privacidad desde el diseño**: autorización obligatoria, enlace público sin datos personales y anonimización auditada que conserva la historia.
5. **Aislamiento entre talleres** probado en cada recurso.
6. **Especificación antes del código** (SPEC y ADR) y **trazabilidad** de cada requisito a la tesis.
7. **Instrumento de investigación listo**: el historial de estados ya guarda las marcas de tiempo que necesita el reporte R2 para responder la pregunta de investigación, y la categoría del problema permitirá saber qué fallas son las más frecuentes.
8. **Evolución del modelo sin perder datos**: las migraciones 0006 y 0007 agregaron el tipo de vehículo y la categoría del problema conservando todos los registros anteriores y la compatibilidad del API.
9. **Constancia del servicio para el cliente**: un informe PDF que el servidor solo genera al entregar y que, en su versión pública, protege los datos personales.

---

## 7. Lo que estos resultados no demuestran todavía

| Aspecto | Por qué no está demostrado | Cómo se demostrará |
|---|---|---|
| Reducción de los tiempos de atención | No hay piloto ni línea base del proceso en papel | Medir primero en papel y luego con el sistema (Semana 7 en adelante) |
| Usabilidad para talleres informales | No hay usuarios reales todavía | Cuestionario de usabilidad en el piloto |
| Rendimiento con 5.000 órdenes por taller (RNF-03) | No se hizo una prueba de carga | Prueba con datos sintéticos después del despliegue |
| Funcionamiento en la nube y con HTTPS | El despliegue está pendiente | Semana 5 |
