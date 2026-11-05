# Guion completo de sustentación — Taller Digital

| Campo | Valor |
|---|---|
| Para quién | El autor, para leer o presentar ante el jurado |
| Duración total | 15 minutos (9 de exposición + 5 de demostración + 1 de cierre) |
| Base | Commit `e51d187` (04/11/2026) más los ajustes visuales del 05/11/2026 (SPEC §21.11) |
| Material de apoyo | 10 diapositivas sugeridas; demostración en vivo ([guion detallado](05-guion-demostracion.md)) |

**Cómo usar este guion:** el texto entre comillas está escrito para leerse en voz alta, a un ritmo de unas 140 palabras por minuto. Las indicaciones entre corchetes son para usted, no para leer. Si el tiempo se acorta a 10 minutos, use la versión reducida de la sección 10.

| Parte | Tiempo | Diapositiva |
|---|---|---|
| 1. Introducción | 0:00 – 1:00 | 1 |
| 2. Problema | 1:00 – 2:30 | 2 |
| 3. Objetivos | 2:30 – 3:30 | 3 |
| 4. Arquitectura | 3:30 – 5:30 | 4 y 5 |
| 5. Desarrollo | 5:30 – 7:30 | 6 y 7 |
| 6. Demostración | 7:30 – 12:30 | En vivo |
| 7. Resultados | 12:30 – 13:45 | 8 y 9 |
| 8. Conclusiones | 13:45 – 15:00 | 10 |

---

## 1. Introducción — 0:00 a 1:00

**[Diapositiva 1: título del proyecto, su nombre, programa, universidad y asesor.]**

> «Buenos días, honorables jurados. Mi nombre es John Edison Hernández Vargas y presento mi proyecto de grado de Ingeniería de Software: *Prototipo web para la gestión de los procesos operativos en talleres mecánicos de la zona norte de Cali*.
>
> El resultado es Taller Digital: una aplicación web, pensada primero para el celular, que acompaña a un carro o una moto desde que entra al taller hasta que se entrega con su informe final, y que permite al cliente seguir su vehículo desde un enlace.
>
> En los próximos minutos voy a presentar el problema, los objetivos, la arquitectura, cómo lo desarrollé, una demostración en vivo, los resultados y, con la misma claridad, lo que todavía falta.»

---

## 2. Problema — 1:00 a 2:30

**[Diapositiva 2: cuatro íconos — cuaderno, mecánico, estante de repuestos, cliente con teléfono — y las cifras 9 %, 85 % y 78 %.]**

> «En Colombia se estima que apenas el 9 % de los talleres mecánicos usa software especializado. En las comunas 2, 4, 5 y 6 de Cali, con alta densidad vehicular y un parque automotor envejecido, la mayoría de talleres pequeños y medianos lleva su operación en cuadernos y en conversaciones de WhatsApp.
>
> En la fase de diagnóstico visitamos diez talleres, ocho formales y dos informales, y encuestamos a 384 clientes. Encontramos cuatro problemas concretos:
>
> Primero, cuellos de botella al recibir los carros, con datos incompletos.
> Segundo, la información se pierde entre recepción y el mecánico: nadie sabe con certeza quién tiene cada carro ni en qué va.
> Tercero, el inventario se cuenta a mano: los repuestos se acaban sin aviso y no se sabe qué consumió cada trabajo.
> Y cuarto, el cliente no sabe en qué va su carro ni cómo se compone el cobro. El 85 % de los encuestados quiere un canal digital para seguirlo, y el 78 % percibe demoras e informalidad.
>
> De ahí surge nuestra pregunta de investigación: ¿qué impacto tendría un prototipo web en la reducción de los tiempos de respuesta y en la eficiencia de los procesos operativos de estos talleres?»

---

## 3. Objetivos — 2:30 a 3:30

**[Diapositiva 3: objetivo general y los cuatro específicos, con su estado: logrado, logrado, implementación lograda y piloto pendiente, pendiente.]**

> «El objetivo general es desarrollar un prototipo web para la gestión de los procesos operativos de estos talleres.
>
> Los objetivos específicos son cuatro. Diagnosticar los procesos actuales, que se cumplió en la fase de investigación. Diseñar la estructura y los módulos, que se cumplió con una especificación formal y seis decisiones de arquitectura documentadas. Implementar y evaluar con un piloto: la implementación está terminada como producto mínimo viable; la evaluación piloto está pendiente. Y capacitar y recoger retroalimentación, que se hará en el piloto con los manuales que ya preparé.
>
> Quiero ser preciso en esto: hoy presento un software terminado y probado, no todavía los resultados de campo. El sistema ya registra los datos que permitirán medir el impacto.»

---

## 4. Arquitectura — 3:30 a 5:30

**[Diapositiva 4: diagrama de capas — navegador con React; FastAPI con API, servicios y acceso a datos; PostgreSQL.]**

> «La arquitectura es un monolito cliente-servidor por capas. Lo elegí a conciencia: soy un solo desarrollador, sin presupuesto, y el volumen es el de un piloto. Un solo despliegue es más barato, más simple y tiene menos puntos de falla que los microservicios.
>
> El backend está en Python con FastAPI, organizado en tres capas: la API recibe las solicitudes, autentica y valida la entrada; la capa de servicios aplica las reglas de negocio; y el acceso a datos usa SQLAlchemy contra PostgreSQL 17. El frontend es React, y el mismo servidor lo entrega desde el mismo dominio.
>
> Las reglas importantes viven en el servidor, no en la pantalla. Por ejemplo, el servidor le dice a la interfaz qué cambios de estado puede hacer cada usuario, y la interfaz solo muestra esos botones.»

**[Diapositiva 5: tres bloques — Seguridad, Varios talleres, Integridad.]**

> «Tres decisiones de diseño merecen atención.
>
> La seguridad: las claves se guardan con argon2id; la sesión viaja en una cookie que el código de la página no puede leer; los permisos se verifican en el servidor en cada solicitud, leyendo el rol de la base de datos.
>
> Varios talleres en una sola instalación: cada registro lleva el taller al que pertenece, el taller se toma siempre del usuario de la sesión, y si alguien pide algo de otro taller, el sistema responde que no existe. Esto tiene pruebas automatizadas en cada recurso.
>
> Y la integridad en dos niveles: cada regla crítica está en el código y también en la base de datos. Por ejemplo, el stock no puede quedar negativo, un carro no puede tener dos órdenes abiertas y no se registra a un cliente sin su autorización de datos, aunque alguien se saltara la aplicación.»

---

## 5. Desarrollo — 5:30 a 7:30

**[Diapositiva 6: línea de tiempo — Fase 0 y Semana 1 (23/10), Semana 2 (25/10), Semana 3 (25/10), Semana 4 (26/10), Anonimización (28/10), Mejoras tras el MVP (04/11 y 05/11).]**

> «El desarrollo siguió un método guiado por especificación. Antes de escribir código redacté y aprobé un documento de especificación con 26 requisitos funcionales priorizados con MoSCoW, 11 no funcionales y 21 reglas de negocio, cada uno trazado a su fuente en la investigación.
>
> Después construí por cortes verticales semanales: en cada semana, la base de datos, la API y la interfaz de una función completa, con una demostración al final.
>
> La semana uno fueron las fundaciones: acceso, roles y usuarios. La semana dos, clientes y vehículos. La semana tres, el núcleo: órdenes, seis estados con historial y asignación de mecánicos. La semana cuatro completó el flujo: inventario, liquidación y el seguimiento del cliente. Después agregué la anonimización de clientes para cumplir la Ley 1581.
>
> Con el margen que dejó el plan, revisé el MVP y agregué mejoras: carros y motos, una categoría del problema por tipo de vehículo, el informe final en PDF, el registro del cliente con su vehículo en un solo paso y un rediseño de la interfaz. Las nuevas columnas llegaron con migraciones que conservaron todos los datos anteriores.
>
> Cada decisión que surgió en el camino quedó registrada con su identificador: son 58 decisiones documentadas.»

**[Diapositiva 7: los seis estados de la orden y, debajo, «cada cambio = fecha + hora + usuario + nota».]**

> «La decisión de diseño más importante para la investigación es esta: cada cambio de estado guarda el estado anterior, el nuevo, quién lo hizo y cuándo. Agregué el estado *Esperando repuestos*, que no estaba en la tesis original, porque es justamente donde los talleres pierden más tiempo. Con ese historial se calculará el tiempo promedio de cada etapa, que es la medida objetiva que responde la pregunta de investigación.
>
> Ahora les muestro el sistema funcionando.»

---

## 6. Demostración — 7:30 a 12:30

**[Cambie a las ventanas preparadas según el [guion de demostración](05-guion-demostracion.md). En esta versión de 5 minutos, haga solo los pasos indicados.]**

| Tiempo | Qué hacer | Qué decir (resumido) |
|---|---|---|
| 7:30 | Recepción ya dentro. **Clientes → + Cliente** «Marta Ríos (demo)» y, en el mismo formulario, el carro «dem-432» → DEM432. Intente guardar sin autorización, luego márquela. | «Cliente y carro se guardan juntos o ninguno. Sin autorización no se registra: está en la base de datos. La placa se normaliza.» |
| 8:30 | **Nueva orden para este carro**: categoría escribiendo «fren» → **Problemas de frenos**, observación, kilometraje, Mecánico Norte → **Abrir orden**. **Copiar enlace** y ábralo en el celular. | «Tres pasos para recibir un carro. La categoría sale de un catálogo para carros y otro para motos. Este enlace es lo que recibe la clienta.» |
| 9:15 | Ventana del mecánico (vista de celular): **Iniciar diagnóstico** → **Esperando repuestos** con nota. Actualice el celular del cliente. | «El mecánico ve solo sus órdenes. Cada cambio queda con su nombre y hora; la clienta ya lo ve.» |
| 10:00 | Mecánico: **+ Repuesto** filtro W712 cantidad 5 → error «quedan 2»; cantidad 1. **+ Mano de obra** 60.000. Trabajo realizado → **Marcar reparado**. | «El stock nunca queda negativo, ni con operaciones simultáneas. El precio queda congelado en la orden.» |
| 10:45 | Recepción: muestre el total calculado → **Entregar** → **Descargar informe PDF**. Actualice el celular: «Su carro ya fue entregado», placa DEM*** y su propio botón de informe. | «El total lo calcula el servidor, sin IVA. El informe solo existe al entregar, y lo valida el servidor. La clienta no ve ningún dato personal, tampoco en su PDF.» |
| 11:30 | Administrador: **Clientes → Marta Ríos → Anonimizar**, escriba ANONIMIZAR. Muestre el aviso de auditoría, la orden conservada y el enlace que sigue funcionando. | «Se borran sus datos personales y se conserva la historia del taller. Solo el administrador, con confirmación escrita, y queda registrado quién y cuándo.» |

**[Vuelva a las diapositivas a las 12:30.]**

---

## 7. Resultados — 12:30 a 13:45

**[Diapositiva 8: cifras — 15 de 17 requisitos *Must* completos, 21 de 21 reglas de negocio, 263 pruebas automatizadas, 91 % de cobertura del backend, 3 pruebas de concurrencia, 12 tablas y 7 migraciones, 38 operaciones de API, $0.]**

> «Estos son los resultados del desarrollo.
>
> De los 17 requisitos obligatorios, 15 están completos, el dashboard está en una versión mínima y los reportes están pendientes. Las 21 reglas de negocio están implementadas.
>
> El sistema tiene 263 pruebas automatizadas que pasan contra PostgreSQL real y cubren el 91 % del backend, incluidas pruebas de concurrencia para el número de orden y para el stock, y pruebas de aislamiento entre talleres en cada recurso. Además, cada semana cerró con una validación funcional; la del flujo completo pasó 32 de 32 verificaciones.
>
> En el camino resolví problemas reales de ingeniería, como la concurrencia en el consecutivo y en el inventario, o la protección contra la enumeración de correos en el inicio de sesión.»

**[Diapositiva 9: dos columnas — «Pendiente antes de la sustentación» y «Trabajo futuro».]**

> «Y quiero ser transparente con lo que falta. Pendiente para las próximas semanas: el despliegue en la nube con HTTPS, en Render y Neon; el reporte de tiempo promedio por etapa, que es la evidencia central de la tesis; y el refuerzo de seguridad, como el límite de intentos de inicio de sesión y las cabeceras de seguridad.
>
> Y lo más importante: el piloto en al menos tres talleres, midiendo primero el proceso en papel para tener contra qué comparar. Hasta entonces, no afirmo una reducción de tiempos: afirmo que el sistema está listo para medirla.»

---

## 8. Conclusiones — 13:45 a 15:00

**[Diapositiva 10: tres conclusiones y «Gracias».]**

> «Para concluir, tres ideas.
>
> Primera: el prototipo cumple el objetivo general. Cubre el flujo operativo completo de un taller, desde la recepción hasta la entrega, con el cliente informado y desde un celular.
>
> Segunda: se construyó con criterios de ingeniería verificables: una especificación antes del código, decisiones documentadas, integridad garantizada en dos niveles y pruebas automatizadas, incluidas las de concurrencia y aislamiento.
>
> Tercera: respeta la ley de protección de datos desde el diseño: autorización obligatoria, un enlace público sin datos personales y una anonimización que borra a la persona sin borrar la historia del taller.
>
> El aporte principal es que el sistema convierte la operación del taller en datos medibles. El siguiente paso, el piloto, permitirá responder la pregunta de investigación con datos y no con percepciones.
>
> Muchas gracias. Quedo atento a sus preguntas.»

---

## 9. Diapositivas sugeridas

| N.º | Título | Contenido |
|---|---|---|
| 1 | Taller Digital | Título del proyecto, autor, programa, universidad, asesor, fecha |
| 2 | El problema | 4 problemas con ícono; cifras 9 %, 85 %, 78 %; pregunta de investigación |
| 3 | Objetivos | General y OE1 a OE4 con su estado |
| 4 | Arquitectura | Diagrama de capas (del [manual técnico](03-manual-tecnico.md), §1.1) |
| 5 | Decisiones clave | Seguridad · Varios talleres · Integridad en dos niveles |
| 6 | Cómo se construyó | Línea de tiempo por semanas con commits |
| 7 | La orden y su trazabilidad | Diagrama de 6 estados; «fecha + hora + usuario + nota» |
| 8 | Resultados | Cifras del desarrollo |
| 9 | Lo que falta | Pendiente (Semana 5–6, piloto) y trabajo futuro |
| 10 | Conclusiones | Tres conclusiones y «Gracias» |

Use poco texto por diapositiva: el detalle está en lo que usted dice. Ponga los diagramas grandes.

---

## 10. Versión reducida (10 minutos)

| Parte | Tiempo | Cambio |
|---|---|---|
| Introducción | 0:00 – 0:40 | Solo el primer y el último párrafo |
| Problema | 0:40 – 1:40 | Las cifras y los cuatro problemas en una frase cada uno |
| Objetivos | 1:40 – 2:20 | General, y una frase sobre el estado de OE3 |
| Arquitectura | 2:20 – 3:40 | Solo la diapositiva 5 |
| Desarrollo | 3:40 – 4:40 | Solo la diapositiva 7 |
| Demostración | 4:40 – 8:10 | Orden ya abierta: estados → repuesto con error de stock → entrega → informe PDF → enlace → anonimización |
| Resultados | 8:10 – 9:10 | Diapositiva 8 y una frase sobre lo pendiente |
| Conclusiones | 9:10 – 10:00 | Las tres conclusiones |

---

## 11. Recordatorios para el momento de hablar

- Diga **«prototipo validado en entorno local»**, no «sistema en producción».
- Diga **«el sistema registra los datos para medir el impacto»**, no «el sistema redujo los tiempos».
- Si preguntan por algo pendiente, responda con el plan: qué, cuándo y cómo. Ver las [preguntas probables](06-preguntas-jurado.md).
- Tenga a mano la [matriz de requisitos](07-matriz-requisitos.md) por si piden el estado de un requisito específico.
- Si la demostración falla, pase a las capturas del plan B sin detenerse a depurar.
