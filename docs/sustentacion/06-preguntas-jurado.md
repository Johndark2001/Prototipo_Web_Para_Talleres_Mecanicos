# Preguntas probables del jurado — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | El autor, como preparación para la sustentación |
| Corte | Commit `e51d187` (04/11/2026) más los ajustes visuales del 05/11/2026 (SPEC §21.11) |
| Total | 72 preguntas en 9 categorías |

**Regla de oro:** si la respuesta es «todavía no», dígalo así y explique cuándo y cómo se hará. El jurado valora más la honestidad sobre el alcance que una respuesta adornada.

---

## 1. Negocio (8)

**1. ¿Qué problema resuelve el sistema?**
Los talleres pequeños y medianos de la zona norte de Cali gestionan las órdenes, el inventario y el historial en cuadernos y WhatsApp. Eso produce cuellos de botella al recibir carros, pérdida de información entre recepción y mecánico, inventario descuadrado y cobros poco transparentes. El sistema digitaliza ese ciclo completo y le da al cliente un enlace para seguir su carro.

**2. ¿Por qué un taller pequeño o informal lo usaría, si ya le funciona el cuaderno?**
Porque le resuelve tres dolores concretos que encontramos en el diagnóstico: saber en qué va cada carro y quién lo tiene, no quedarse sin repuestos sin aviso y dejar de recibir llamadas de clientes preguntando por su carro. Además el sistema está diseñado para el celular, con pocos campos y el vocabulario del taller. Que lo adopten de verdad es algo que se evaluará en el piloto.

**3. ¿Qué evidencia hay de que los clientes lo quieren?**
La encuesta de la investigación a 384 clientes: el 85 % quiere un canal digital para seguir el estado de su vehículo y el 78 % percibe demoras e informalidad en los registros en papel. Por eso el seguimiento público (RF-13) es un requisito *Must*.

**4. ¿Cuánto le cuesta al taller?**
La infraestructura prevista cuesta $0: planes gratuitos de Render y Neon (P-6, RNF-11). Hoy el sistema corre en local, también sin costo. Un modelo comercial no forma parte del alcance de la tesis.

**5. ¿Por qué no factura ni calcula IVA?**
La facturación electrónica de la DIAN implica requisitos tributarios, certificación y un proveedor tecnológico. Eso está fuera del alcance de un prototipo académico (SPEC §2.2, P-9). La liquidación transparenta el cobro, pero no reemplaza la factura.

**6. ¿Por qué el cliente no tiene usuario y contraseña?**
Porque es una barrera de adopción: el cliente no va a crear una cuenta para un taller que visita dos veces al año. Usa un enlace único por orden, con un código aleatorio de 128 bits imposible de adivinar (P-4, ADR-005).

**7. ¿Por qué no envía notificaciones automáticas por WhatsApp?**
La API de WhatsApp Business tiene costo y requiere aprobación. El SPEC prevé un botón que abre WhatsApp con el mensaje ya escrito (RF-20), pero quedó aplazado (S4-7). Hoy el enlace se copia con un botón y se pega en la conversación.

**8. ¿Qué ventaja tiene sobre un software comercial de talleres?**
Está diseñado para el contexto específico de la zona norte de Cali: talleres formales e informales, uso desde el celular y costo cero. También cumple la Ley 1581 desde el diseño. No pretende competir en funciones con un ERP comercial: es un prototipo para validar el impacto en los tiempos.

---

## 2. Arquitectura (8)

**9. ¿Qué arquitectura usó y por qué?**
Un monolito cliente-servidor por capas con una API REST JSON (ADR-001). Las capas son API, servicios, acceso a datos y PostgreSQL. Lo elegí porque soy un solo desarrollador, sin presupuesto, y el volumen es el de un piloto. Un solo despliegue reduce los puntos de falla y el costo.

**10. ¿Por qué no microservicios?**
Agregan complejidad operativa (red, despliegues múltiples, consistencia distribuida) sin ningún beneficio para este volumen ni para un equipo de una persona. El SPEC los prohíbe explícitamente (§16).

**11. ¿Por qué FastAPI y no Django o Node?**
FastAPI valida la entrada con tipos (Pydantic), genera la documentación OpenAPI automáticamente y es ligero. Python era el lenguaje en el que tenía más experiencia (ADR-002). Django trae un administrador y un ORM propios que no necesitábamos.

**12. ¿Por qué React?**
Permite construir una interfaz dinámica que cambia según el rol y el estado de la orden, con componentes reutilizables. Como era el mayor riesgo de aprendizaje, el ADR-004 tenía un punto de control en la primera semana y un plan B con plantillas Jinja. El plan B no hizo falta.

**13. ¿Cómo se comunican el frontend y el backend?**
Por la API REST en `/api/v1` con JSON. Comparten el mismo dominio: en producción el backend sirve la interfaz compilada y, en desarrollo, Vite reenvía `/api` al backend. Por eso la cookie de sesión funciona sin configurar CORS.

**14. ¿Dónde están las reglas de negocio?**
En la capa de servicios del backend. La interfaz no decide nada importante: el servidor le envía qué transiciones de estado puede hacer el usuario y qué puede editar, y la interfaz solo muestra esos botones. Las reglas críticas tienen además una segunda barrera en la base de datos.

**15. ¿Cómo maneja varios talleres?**
Con un modelo multi-tenant de base y esquema compartidos y aislamiento lógico por `taller_id` (ADR-006). El taller sale siempre del usuario de la sesión, nunca de la solicitud. Toda consulta lo filtra, y un recurso de otro taller responde «no encontrado». Cada recurso tiene pruebas de aislamiento.

**16. ¿Qué pasa si crece a cientos de talleres?**
La arquitectura ya admite varios talleres en una instalación. Para escalar habría que pasar a un plan de pago sin suspensión, llevar el límite de solicitudes de memoria a un almacén compartido, medir los índices con datos reales y evaluar Row-Level Security de PostgreSQL como segunda barrera. Está documentado como trabajo futuro.

---

## 3. Base de datos (8)

**17. ¿Por qué PostgreSQL?**
Es relacional, libre, robusto en transacciones y bloqueos, y soporta índices únicos parciales, restricciones CHECK y `NUMERIC` exacto, que el modelo usa. Además hay planes gratuitos administrados (Neon). Está en el ADR-003.

**18. ¿Cuántas tablas tiene el modelo y cuáles son las principales?**
Doce. Las tablas raíz son `taller`, `usuario`, `cliente`, `vehiculo`, `orden_trabajo`, `servicio` y `repuesto`. Las tablas hijas son `historial_estado_orden`, `asignacion_orden`, `orden_servicio`, `orden_repuesto` y `movimiento_inventario`. La factura y el historial del carro no tienen tabla: se calculan.

**19. ¿Cómo garantiza que el stock nunca sea negativo?**
En dos niveles. Primero, en el servicio, la fila del repuesto se bloquea (`SELECT … FOR UPDATE`) y el descuento, el movimiento y la línea se guardan en una sola transacción. Segundo, la base tiene `CHECK stock_actual >= 0`. Hay una prueba de concurrencia que lanza registros simultáneos y verifica que nunca quede negativo.

**20. ¿Cómo evita que un carro tenga dos órdenes abiertas?**
Con un índice único parcial sobre el vehículo, que solo aplica a las órdenes que no están entregadas ni canceladas (RN-08). Aunque dos recepcionistas lo intenten al mismo tiempo, la base de datos solo deja crear una; está probado.

**21. ¿Por qué guarda el precio en cada línea en lugar de leerlo del catálogo?**
Porque el precio cambia con el tiempo. Si la orden leyera el precio actual, una orden vieja cambiaría de valor. Cada línea guarda una copia del precio del momento (RN-05).

**22. ¿Por qué no guarda el total de la orden?**
Para no tener dos fuentes de verdad. El total se calcula siempre como la suma de cantidad × precio de las líneas (RN-06), en el servidor y con decimales exactos. Nunca se acepta un total enviado desde el navegador.

**23. ¿Cómo maneja los cambios en la estructura de la base?**
Con migraciones versionadas de Alembic: hay siete, de la 0001 a la 0007, y cada una tiene su reversión. Las dos últimas muestran cómo se cambia el modelo sin perder datos: la 0006 agrega el tipo de vehículo y deja los existentes como carros, y la 0007 agrega la categoría del problema y copia el motivo anterior a la observación del cliente. La suite de pruebas aplica todas las migraciones desde cero en cada ejecución, así que también se prueban.

**24. ¿Usó SQLite para las pruebas?**
No. Las pruebas corren contra PostgreSQL real, en una base exclusiva que se vacía en cada prueba. SQLite no tiene los mismos bloqueos, índices parciales ni restricciones, y las pruebas no habrían demostrado lo mismo.

---

## 4. Seguridad (8)

**25. ¿Cómo se guardan las contraseñas?**
Con hash argon2id, el algoritmo recomendado actualmente, resistente a ataques con GPU. Nadie puede ver la clave original. Hay una prueba que verifica que el hash guardado es argon2id.

**26. ¿Cómo funciona la sesión?**
Al iniciar sesión, el servidor firma un JWT con el id del usuario y lo envía en una cookie `httpOnly` con `SameSite=Lax`; en producción, además, `Secure`. El JavaScript de la página no puede leerla. La sesión dura 8 horas. En cada solicitud el servidor vuelve a leer al usuario de la base: si lo desactivan, pierde el acceso al instante.

**27. ¿Por qué no guarda el token en localStorage?**
Porque cualquier script que logre ejecutarse en la página, por ejemplo por un XSS, podría robarlo. La cookie `httpOnly` no es accesible desde JavaScript. El SPEC lo prohíbe (§16).

**28. ¿Cómo se protege contra CSRF?**
Con `SameSite=Lax` en la cookie y un middleware que rechaza con 415 toda modificación que no venga en JSON: un formulario HTML de otro sitio no puede enviar JSON. Hay una prueba para eso.

**29. ¿Cómo evita que alguien adivine qué correos están registrados?**
El mensaje es siempre «Correo o clave incorrectos». Además, si el correo no existe, la clave se verifica contra un hash ficticio para que la respuesta tarde lo mismo.

**30. ¿Cómo se verifican los permisos?**
En el servidor, en cada solicitud. El rol se lee de la base de datos, nunca del token ni de lo que envía el navegador. Si el rol no tiene permiso, la respuesta es 403. Las rutas protegidas de la interfaz son solo comodidad.

**31. ¿Tiene HTTPS?**
**Todavía no**, porque el sistema aún no está desplegado. Llega en la Semana 5 con Render, que da HTTPS automático. El código ya marca la cookie como `Secure` cuando `ENTORNO=produccion`.

**32. ¿Qué le falta en seguridad?**
Está planificado para la Semana 5: el límite de intentos de inicio de sesión, las cabeceras de seguridad (CSP y HSTS), la auditoría de dependencias, el cambio y la recuperación de clave, y tomar la IP real detrás del proxy para el límite del seguimiento. Lo mínimo no se recortó desde la primera semana: argon2id, cookie httpOnly, filtro por taller, validación de la entrada y consultas parametrizadas.

---

## 5. Desarrollo (8)

**33. ¿Cómo organizó el desarrollo?**
Primero una especificación aprobada (SPEC y seis ADR, Fase 0) y después cortes verticales semanales: base de datos, API e interfaz de cada función a la vez. Cada semana terminaba con una demostración y la aprobación del autor, y las decisiones se registraron en el SPEC.

**34. ¿Cuántas pruebas tiene y qué cubren?**
263 pruebas automatizadas, todas pasan: 200 funciones, algunas parametrizadas, en 16 archivos. Cubren autenticación, permisos, aislamiento entre talleres, transiciones de estado, stock, liquidación, seguimiento, anonimización, tipo de vehículo, categoría del problema, informe PDF y alta de cliente con vehículo, más tres pruebas de concurrencia. La cobertura del backend es del 91 %, y del 97 % sin contar los dos scripts de consola.

**35. ¿Por qué no hay pruebas automatizadas de la interfaz?**
Por el tamaño del equipo, quedaron fuera de alcance (SPEC §15). La interfaz se validó con una lista de verificación manual por pantalla: cuatro anchos, teclado y los estados vacío, de error y de carga. En la Semana 4 hubo una validación de punta a punta con 32 de 32 verificaciones.

**36. ¿Cuál fue el problema técnico más difícil?**
La concurrencia: que dos recepcionistas no saquen el mismo número de orden y que dos mecánicos no dejen el stock negativo. Se resolvió con bloqueos de fila, restricciones en la base y pruebas que lanzan operaciones simultáneas. También aprendí que PostgreSQL no permite `FOR UPDATE` sobre el lado opcional de un `LEFT JOIN`, y ajusté las consultas.

**37. ¿Cómo garantiza la calidad del código?**
Con Ruff (estilo y formato de Python), ESLint (JavaScript), tipos en las funciones públicas y pytest antes de cada commit. Los comentarios explican el porqué, y los nombres están en español del dominio, igual que en la tesis.

**38. ¿Cómo se implementan los estados de la orden?**
Como una máquina de estados de reglas puras (`flujo_orden.py`), sin base de datos, que decide qué transición existe y quién puede hacerla. Las condiciones que dependen de los datos (mecánico asignado, trabajo realizado, motivo) se verifican en el servicio. Cada cambio inserta un registro en el historial.

**39. ¿Usó inteligencia artificial para desarrollar?**
Sí, me apoyé en un asistente de programación (Claude Code) bajo un proceso controlado: yo definí y aprobé la especificación, las decisiones (registradas en el SPEC con su identificador) y cada entrega semanal antes del commit, y validé manualmente cada función. Los commits lo declaran como coautor. La responsabilidad de las decisiones y de la validación es mía. *(Ajuste esta respuesta a lo que usted declare formalmente en la tesis.)*

**40. ¿El código es mantenible por otra persona?**
Sí. Tiene especificación, ADR, modelo de datos documentado, un README de puesta en marcha, un manual técnico, convenciones explícitas y pruebas que funcionan como documentación viva de las reglas.

---

## 6. Gestión de proyecto (8)

**41. ¿Cumplió el cronograma?**
El plan vigente preveía el MVP en 4 semanas, del 26/10 al 22/11/2026. Las cuatro semanas funcionales quedaron cerradas entre el 23 y el 26/10, y la anonimización el 28/10. Con ese margen, el 04/11 y el 05/11 incorporé mejoras pedidas tras revisar el MVP (tipo de vehículo, categoría del problema, informe PDF, alta de cliente con vehículo, rediseño), todas registradas como decisiones en el SPEC. Lo único que se movió fue el despliegue, que pasó a la Semana 5 por la decisión S4-8, como preveía el plan de recortes.

**42. ¿Qué metodología siguió?**
Desarrollo guiado por especificación con entregas incrementales semanales (cortes verticales), priorización MoSCoW de los requisitos y aprobación explícita de cada fase. No es Scrum formal porque el equipo es de una persona, pero tomé su idea de entregas cortas y demostrables.

**43. ¿Cómo priorizó los requisitos?**
Con MoSCoW: 17 *Must*, 4 *Should* y 5 *Could*. Además definí un orden de recortes por si había atrasos y una lista de lo que nunca se recorta: los estados, los repuestos en la orden, la liquidación, el seguimiento, el aislamiento y la seguridad mínima.

**44. ¿Qué riesgos identificó y cómo los manejó?**
El SPEC tiene 13 riesgos. Los principales: el plazo para un solo desarrollador (cortes verticales y recortes previstos), la curva de React (punto de control con plan B), la fuga de datos entre talleres (ADR-006 y pruebas), el stock inconsistente (bloqueos) y el riesgo académico de presentar como hechos resultados aún no medidos (R-01), que manejo separando con claridad lo implementado de lo pendiente.

**45. ¿Por qué no está desplegado si era parte de la Semana 4?**
El despliegue requiere crear cuentas en Render y Neon y ajustar el límite por IP detrás del proxy. El plan ya preveía como recorte 4 pasar el despliegue a la Semana 5 y validar en local. Se aplicó con la decisión S4-8, sin afectar ninguna función.

**46. ¿Qué haría distinto?**
Desplegaría un esqueleto en la nube desde la primera semana, como recomendaba el propio plan, para eliminar ese riesgo pronto. Y escribiría la guía rápida del piloto en paralelo con el desarrollo.

**47. ¿Cómo controló el alcance?**
Todo cambio pasa primero por el SPEC (§16, «actualizar el SPEC antes de cambiar una decisión»). Las ideas nuevas se clasificaron como *Should* o *Could* o quedaron fuera de alcance. Por ejemplo, el catálogo de servicios, el botón de WhatsApp y el historial en el enlace se aplazaron con decisiones registradas.

**48. ¿El piloto con 10 talleres es viable?**
Para una sola persona, no (riesgo R-12). El criterio de éxito es un mínimo de 3 talleres (2 formales y 1 informal), midiendo primero el proceso en papel. La tesis se ajustará en ese punto (H-3).

---

## 7. Protección de datos (8)

**49. ¿Cómo cumple la Ley 1581 de 2012?**
De cinco maneras: autorización obligatoria con fecha antes de registrar a un cliente (en la API y en la base), datos mínimos (correo y documento opcionales), enlace público sin datos personales, aislamiento entre talleres y anonimización para el derecho de supresión. Además, hasta el piloto solo se usan datos ficticios (H-5).

**50. ¿Qué datos personales guarda?**
Del cliente: nombre, teléfono, correo y documento (los dos últimos opcionales), además de la autorización y su fecha. Del usuario del taller: nombre, correo y el hash de la clave. No se guardan fotos, direcciones ni datos financieros.

**51. ¿Qué pasa si el cliente no autoriza?**
No se registra. El sistema lo rechaza en la interfaz, en la API y en la base de datos (`CHECK autoriza_datos = true`). El taller puede atender el carro, pero no registrarlo en el sistema a nombre de esa persona.

**52. ¿Qué ve quien tenga el enlace de seguimiento?**
El taller, el número de orden, la placa enmascarada (ABC***), la marca y el modelo, el estado, la línea de tiempo y el cobro. Nada más: no ve el nombre, el teléfono, el documento, el correo, el kilometraje, el motivo, las notas ni los empleados. El servidor usa una lista blanca de campos y una prueba lo verifica. Cuando la orden se entrega, puede descargar además el informe PDF, que tampoco trae nombre, teléfono ni kilometraje y lleva la placa enmascarada; sí trae la categoría, la observación, el diagnóstico y el trabajo realizado (pregunta 67).

**53. ¿Y si alguien prueba códigos al azar?**
El código tiene 128 bits aleatorios, así que adivinarlo es inviable. Además hay un límite de 30 consultas por minuto por IP y un código mal formado ni siquiera llega a la base.

**54. ¿Puede un taller ver los clientes de otro?**
No. Todo se filtra por el taller del usuario de la sesión y un recurso ajeno responde «no encontrado». Cada recurso tiene pruebas de aislamiento, y la semilla de demostración tiene la misma placa en dos talleres a propósito para verificarlo a mano.

**55. ¿Dónde estarán alojados los datos y con qué protección?**
En el despliegue previsto: la aplicación en Render y la base en Neon, con HTTPS entre el navegador y la aplicación y SSL entre la aplicación y la base. Hoy está en local. Falta definir la política de respaldos y su tiempo de conservación (Semana 5).

**56. ¿Usó datos reales?**
No. En desarrollo y en demostraciones solo hay datos ficticios, marcados con «(demo)» (H-5). Los datos reales se usarán solo en el piloto, con la autorización de los talleres y de sus clientes.

---

## 8. Anonimización (8)

**57. ¿Por qué anonimizar en lugar de borrar al cliente?**
Porque borrarlo rompería la historia operativa: sus órdenes, el inventario consumido, los cobros y los tiempos por etapa, que además son la evidencia de la investigación. La regla RN-11 dice que la historia nunca se borra. La anonimización elimina lo que identifica a la persona y conserva lo operativo.

**58. ¿Qué datos se anonimizan exactamente?**
El nombre (pasa a «Cliente anonimizado N.º id»), el teléfono (vacío), el correo y el documento (nulos). El cliente queda inactivo. Se conservan la autorización y su fecha, como prueba de que el dato se trató con permiso (A-3).

**59. ¿Quién puede anonimizar y cómo se evita un error?**
Solo el administrador. Debe escribir la palabra ANONIMIZAR en un diálogo que explica las consecuencias, y la API también exige esa palabra, así que no basta con un clic. No se permite si el cliente tiene órdenes abiertas (A-1).

**60. ¿Queda registro de quién lo hizo?**
Sí: `anonimizado_por` (el usuario) y `anonimizado_en` (la fecha y hora de la base). Se muestra en el detalle del cliente. Una restricción CHECK de la base garantiza que un cliente anonimizado siempre tenga quién y cuándo, no conserve correo ni documento y esté inactivo (A-7).

**61. ¿Se puede deshacer?**
No, y es a propósito (A-4): si se pudiera deshacer, los datos no estarían realmente borrados. Si la persona vuelve, se registra como cliente nuevo con una nueva autorización, y su documento queda libre para ese registro.

**62. ¿El seguimiento sigue funcionando después de anonimizar?**
Sí. El enlace nunca mostró datos personales, así que no cambia. Lo verifican una prueba automatizada y la validación manual.

**63. ¿La placa no es un dato personal?**
La placa identifica al vehículo, no directamente a la persona, y sostiene el historial del carro, que puede cambiar de propietario. Por eso no se anonimiza (A-5). En el enlace público sí va enmascarada. Si un análisis jurídico la considerara dato personal, se podría extender la anonimización.

**64. ¿Qué limitaciones tiene la anonimización?**
Tres, documentadas. Primero, los textos libres de las órdenes (observación del cliente, diagnóstico, trabajo, notas) no se modifican: si alguien escribió allí datos personales, quedan (A-6), y como la observación, el diagnóstico y el trabajo también salen en el PDF público, la instrucción al taller de no escribirlos es más importante. Segundo, la auditoría está en el propio cliente y no en una tabla general (A-7). Tercero, las copias de seguridad anteriores a la anonimización conservan los datos hasta que venzan: falta definir su política de conservación en el despliegue.

---

## 9. Cambios recientes: carros y motos, categorías, informe PDF e interfaz (8)

**65. ¿Por qué distinguir carros de motos?**
Porque un taller puede recibir carros y motos, y los problemas típicos no son los mismos: una moto tiene cadena y kit de arrastre; un carro, aire acondicionado y alineación. El tipo es obligatorio (V-1), filtra la lista de vehículos (V-3) y decide qué categorías del problema se ofrecen. La migración 0006 dejó los vehículos existentes como carros, sin perder datos.

**66. ¿Por qué el informe PDF se genera en el servidor y no en el navegador?**
Para que la regla «solo existe si la orden está entregada» la haga cumplir el servidor y quede cubierta por pruebas automatizadas: una orden abierta o cancelada responde 409. Usé fpdf2, que es Python puro y no necesita programas instalados en el servidor, algo importante para un plan gratuito (O-4). Fue una dependencia nueva y la registré como decisión, como exige el SPEC §16.

**67. ¿El PDF público no contradice la regla de no mostrar datos en el enlace?**
Es una excepción acotada y aprobada (O-3). El PDF público sigue sin nombre, teléfono ni kilometraje, y con la placa enmascarada. Sí incluye la categoría, la observación, el diagnóstico y el trabajo, porque es la constancia del servicio ya terminado: solo existe cuando la orden fue entregada. El riesgo es que el taller escriba datos personales en esos textos; por eso los manuales lo advierten.

**68. ¿Por qué las categorías son un catálogo fijo y no texto libre?**
Para poder contar después cuáles son los problemas más frecuentes, que es información útil para el taller y para la tesis. Son 22 categorías para carro y 20 para moto, con «Otro» y su descripción obligatoria para lo que no encaje. Se guarda el nombre y no un código: si mañana cambia el catálogo, las órdenes viejas y sus PDF no cambian (O-5). La observación del cliente queda aparte, con sus palabras.

**69. ¿Qué pasó con las órdenes que ya tenían «motivo de ingreso»?**
La migración 0007 copió el motivo a la observación del cliente y las dejó «Sin categoría»; no se perdió nada. La columna `motivo_ingreso` se conserva y ahora se compone como «categoría — observación», y el API todavía acepta la forma anterior (O-6). Es una forma de evolucionar el modelo sin romper lo que ya funcionaba.

**70. ¿Cómo se garantiza que el cliente y su vehículo se guarden juntos?**
Con una sola transacción en el servidor (O-8). Si la placa ya existe o un dato del vehículo es inválido, no se guarda ni el cliente ni el vehículo, y el error indica el campo exacto. Hay pruebas para el caso feliz, para el registro sin vehículo y para la placa repetida.

**71. ¿Por qué la interfaz dice «Cliente» y no «Dueño»?**
Porque quien lleva el vehículo al taller no siempre es su propietario: puede ser un familiar, un conductor o un empleado. Fue un cambio solo de interfaz (T-1): el modelo ya se llamaba `cliente` y las reglas de cambio de titularidad (RN-21) siguen igual.

**72. ¿Los fondos ilustrados no afectan la accesibilidad?**
Es un compromiso que tomé de forma consciente (T-3). Los fondos son SVG decorativos, ocultos para los lectores de pantalla y sin clics. Las tarjetas, listas y formularios son opacos, así que su contraste no cambia. Elegí una opacidad del 50 % para que la identidad del taller se note. Con ese valor, un texto gris que quede justo sobre una línea del dibujo baja a un contraste de cerca de 3:1, por debajo del 4,5:1 que pide RNF-07. Está registrado como limitación y se puede corregir bajando la opacidad sin tocar nada más.
