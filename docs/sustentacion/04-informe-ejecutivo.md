# Informe ejecutivo del proyecto — Taller Digital

| Campo | Valor |
|---|---|
| Título | Prototipo web para la gestión de los procesos operativos en talleres mecánicos de la zona norte de Cali |
| Autor | John Edison Hernández Vargas — Ingeniería de Software, Corporación Universitaria Iberoamericana |
| Para quién | Jurados y docentes |
| Corte del informe | 05/11/2026 — commit `e51d187` más los ajustes visuales del 05/11/2026 (SPEC §21.11) |

---

## 1. Problema identificado

Los talleres mecánicos pequeños y medianos de las comunas 2, 4, 5 y 6 de Cali trabajan, en su mayoría, con **cuadernos, hojas sueltas y mensajes de WhatsApp** sin estructura. Según la fuente citada en la tesis, solo cerca del **9 %** de los talleres del país usa software especializado.

El diagnóstico de la investigación (entrevistas semiestructuradas y observación en 10 talleres —8 formales y 2 informales— y una encuesta a 384 clientes) identificó:

| Problema | Consecuencia |
|---|---|
| Recepción en papel | Cuellos de botella al recibir carros; datos incompletos |
| Asignación empírica del trabajo | El taller no sabe quién tiene cada carro; la información se pierde entre recepción y mecánico |
| Inventario contado a mano | No se sabe qué se consumió; faltan repuestos sin aviso |
| Historial disperso | No se encuentra qué se le hizo antes a un carro |
| Cobros poco transparentes | Desconfianza del cliente |
| Comunicación por llamadas | El cliente no sabe en qué va su carro; el **85 %** de los encuestados pide un canal digital y el **78 %** percibe demoras e informalidad |

**Pregunta de investigación:** ¿qué impacto tendría un prototipo web en la reducción de los tiempos de respuesta y en la eficiencia y eficacia de los procesos operativos de estos talleres?

## 2. Solución desarrollada

**Taller Digital** es una aplicación web, pensada primero para el celular, que digitaliza el ciclo completo de un carro o una moto en el taller:

```
Cliente + vehículo → Orden de trabajo (categoría del problema) → Mecánico → Estados → Repuestos e inventario → Liquidación → Entrega e informe PDF → Seguimiento del cliente
```

Rasgos principales:
- **Trazabilidad total:** cada cambio de estado, asignación, repuesto y movimiento de inventario queda con fecha, hora y usuario. Esos datos permitirán medir los tiempos de cada etapa, que son la evidencia que pide la pregunta de investigación.
- **Recepción estructurada:** cada orden registra una **categoría del problema** de un catálogo por tipo de vehículo (22 para carros, 20 para motos) y la **observación del cliente** con sus palabras. Así se podrán contar los problemas más frecuentes.
- **Transparencia para el cliente:** un enlace único por orden, sin cuenta, muestra el estado, la línea de tiempo y el cobro, **sin datos personales**. Al entregar, el cliente descarga un **informe final en PDF**.
- **Carros y motos:** cada vehículo tiene su tipo, la lista se filtra por él y el cliente se registra con su vehículo en un solo paso.
- **Inventario confiable:** el stock se descuenta al usar un repuesto en una orden y **nunca queda negativo**, ni siquiera con operaciones simultáneas.
- **Protección de datos (Ley 1581):** autorización obligatoria con fecha y **anonimización** del cliente que conserva la historia del taller.
- **Varios talleres en una sola instalación**, con sus datos aislados.
- **Costo de infraestructura previsto: $0** (planes gratuitos, P-6).

Arquitectura: monolito por capas con **FastAPI (Python)**, **React** y **PostgreSQL**, documentado en 6 registros de decisiones de arquitectura (ADR).

## 3. Objetivos

| Objetivo | Estado al 05/11/2026 | Evidencia |
|---|---|---|
| **General:** desarrollar un prototipo web para la gestión de los procesos operativos en talleres mecánicos de la zona norte de Cali | **Logrado en su versión MVP funcional**, validado en entorno local | Código en el repositorio, 263 pruebas automatizadas (91 % de cobertura del backend) y validación funcional del autor |
| **OE1:** diagnosticar los procesos operativos actuales | Logrado en la fase de investigación (documentos de la tesis) | `investigacion_completa.md`, `entrevistas_e_instrumentos.md` |
| **OE2:** diseñar la estructura y los módulos | **Logrado** | SPEC.md (26 requisitos funcionales, 11 no funcionales, 21 reglas de negocio), 6 ADR y el modelo de datos de 12 tablas |
| **OE3:** implementar y evaluar con una prueba piloto | **Implementación: lograda (MVP). Evaluación piloto: pendiente** | El piloto con datos reales está planificado después del despliegue (SPEC §17.2) |
| **OE4:** capacitar y recoger retroalimentación | **Pendiente** | Este paquete incluye el manual de usuario (base de la capacitación, RF-21) |

> **Aclaración importante (riesgo R-01).** Los capítulos de resultados de la tesis describen una reducción de tiempos y una mejora en la satisfacción. **Esos resultados todavía no se han medido con este software.** El sistema ya registra los datos necesarios; la medición se hará en el piloto, comparando primero con el proceso en papel.

## 4. Beneficios

### 4.1 Para el taller

| Beneficio | Cómo lo logra el sistema |
|---|---|
| Recepción más ágil | Buscar la placa, elegir la categoría del problema y abrir la orden; desde el vehículo, ya viene elegido. Un cliente nuevo se registra con su vehículo en un solo formulario |
| Saber quién tiene cada carro | Mecánico asignado, carga de trabajo visible y vista «Mis órdenes» |
| Control del inventario | Descuento automático, alertas de stock bajo, entradas y ajustes con motivo |
| Cobro sin errores de suma | Liquidación calculada por el servidor con precios congelados en la orden |
| Historia del carro | Historial de mantenimiento por placa |
| Responsabilidad clara | Todo queda registrado con el usuario que lo hizo |
| Datos para decidir | Tiempos de cada etapa guardados desde el primer cambio de estado y la categoría de cada problema (reportes pendientes) |
| Constancia del servicio | Informe PDF final con diagnóstico, trabajo, repuestos y total |

### 4.2 Para el cliente

- Ve el estado de su carro desde el celular, sin llamar y sin crear una cuenta.
- Ve el desglose de mano de obra y repuestos antes de recoger el carro.
- Al recogerlo, descarga desde el mismo enlace el informe PDF de lo que se le hizo.
- Sus datos personales no aparecen en el enlace ni en el PDF público, y puede pedir que se anonimicen.

### 4.3 Para la investigación

- Produce los datos objetivos (marcas de tiempo por etapa) que responden la pregunta de investigación.
- Su diseño está documentado y es trazable: cada requisito remite a su fuente en la tesis.

## 5. Estado actual

| Aspecto | Estado |
|---|---|
| MVP funcional (flujo completo) | **Terminado y validado en local** por el autor |
| Anonimización (Ley 1581) | **Terminada y aprobada** (28/10/2026) |
| Rediseño visual y tipo de vehículo (carro o moto) | **Terminados y aprobados** (04/11/2026) |
| Informe PDF, categoría del problema, vista vertical de la orden y alta de cliente con vehículo | **Terminados y aprobados** (04/11/2026) |
| Terminología «Cliente» y fondos temáticos por módulo | **Implementados** (05/11/2026), pendientes de commit |
| Pruebas automatizadas | **263 pruebas, todas pasan**, contra PostgreSQL real; 91 % de cobertura del backend |
| Revisión de estilo | Ruff (Python) y ESLint (JavaScript) sin hallazgos |
| Despliegue público con HTTPS | **Pendiente** (Semana 5) |
| Reportes RF-15 | **Pendientes** (Semana 5) |
| Piloto con talleres reales | **Pendiente** (después del despliegue) |
| Datos usados hasta ahora | Solo ficticios (decisión H-5) |

**Cronología real:**

| Fecha | Hito | Commit |
|---|---|---|
| 23/10/2026 | Fase 0 (especificación) aprobada y Semana 1 (fundaciones) | `a314c7c` |
| 25/10/2026 | Semana 2: clientes y vehículos | `e02fcb3` |
| 25/10/2026 | Semana 3: órdenes, estados y asignación | `fb3f819` |
| 26/10/2026 | Semana 4: inventario, liquidación y seguimiento; MVP validado | `ee5c2f4` |
| 28/10/2026 | Anonimización del cliente | `84f20f3` |
| 28/10/2026 | Documentación de sustentación e historial de commits | `e4a164a`, `e4692f8` |
| 04/11/2026 | Rediseño visual y tipo de vehículo (carro o moto) | `e3fc487` |
| 04/11/2026 | Vista vertical de la orden, informe PDF, categoría del problema y alta de cliente con vehículo | `e51d187` |
| 05/11/2026 | Terminología «Cliente» y fondos temáticos por módulo | Sin commit |

El plan preveía el MVP entre el 26/10 y el 22/11/2026. Se completó antes de esa fecha, lo que dejó margen para mejoras pedidas por el autor antes de la Semana 5 y deja margen para el despliegue, los reportes y el piloto antes de la sustentación de diciembre.

## 6. Alcance implementado

**Implementado:** RF-01 a RF-13, RF-16 y RF-17 completos; RF-14 en versión mínima. Además, la anonimización del cliente (RN-11, RNF-06), el tipo de vehículo, la categoría del problema y el alta de cliente con vehículo. RF-23 (liquidación imprimible) queda **parcialmente** cubierto por el informe PDF final, que solo existe para órdenes entregadas.

**Pendiente:** RF-15 (reportes), RF-14 completo, el despliegue con HTTPS, el endurecimiento de seguridad, RNF-09 completo y RF-21 (manual: este paquete es su base).

**Aplazado (Should/Could):** RF-18 a RF-20, RF-22 y RF-24 a RF-26.

**Fuera de alcance:** facturación DIAN e IVA, pagos en línea, cuentas de cliente, notificaciones automáticas, funcionamiento sin conexión, app nativa, adjuntos, contabilidad y varias sedes.

El detalle requisito por requisito está en la [Matriz final de requisitos](07-matriz-requisitos.md).

## 7. Módulos desarrollados

| Módulo | Qué hace | Requisitos |
|---|---|---|
| Acceso y usuarios | Inicio y cierre de sesión, 3 roles, alta, cambio de rol y desactivación | RF-01, RF-02, RF-16 |
| Clientes | Registro con autorización Ley 1581 y, en el mismo paso, su primer vehículo; búsqueda, edición, desactivación y anonimización | RF-03, RN-10, RN-11, O-8 |
| Vehículos | Carros y motos; registro con placa normalizada y única, cambio de cliente, filtro Todos/Carros/Motos combinado con la placa, búsqueda global por placa | RF-04, RN-20, V-1 a V-3 |
| Órdenes de trabajo | Recepción con categoría del problema y observación del cliente, consecutivo por taller, 6 estados con historial, notas obligatorias, vista en una columna | RF-05, RF-06, O-1, O-5 |
| Informe final | PDF de la orden entregada, para el taller y, sin datos personales, para el cliente | RF-23 (parcial), O-2 a O-4 |
| Asignación | Asignar y reasignar mecánico con historial; «Mis órdenes» | RF-07 |
| Historial del vehículo | Todas las órdenes de un carro | RF-11 |
| Inventario | Catálogo, entradas, ajustes por conteo, movimientos y alertas | RF-08, RF-10 |
| Repuestos y mano de obra en la orden | Descuento y devolución automática del stock; precio congelado | RF-09 |
| Liquidación | Mano de obra + repuestos = total, sin IVA, calculado por el servidor | RF-12 |
| Seguimiento público | Enlace sin cuenta, placa enmascarada, sin datos personales, con límite de consultas | RF-13 |
| Inicio (dashboard mínimo) | Órdenes por estado, entregados hoy y alertas de stock | RF-14 (parcial) |
| Varios talleres | Aislamiento por taller probado en cada recurso | RNF-05 |
| Interfaz | Rediseño con logo, ilustraciones y fondos temáticos por módulo; terminología «Cliente» | RF-17, V-4, T-1 a T-3 |

## 8. Trabajo pendiente

| Prioridad | Tarea | Momento |
|---|---|---|
| 1 | Despliegue en Render (aplicación) y Neon (PostgreSQL) con HTTPS, ajustando el límite por IP detrás del proxy | Semana 5 |
| 2 | Reportes RF-15, empezando por **R2: tiempo promedio por etapa**, que es la evidencia de la tesis | Semana 5 |
| 3 | Seguridad: límite de intentos de login, cabeceras y auditoría de dependencias | Semana 5 |
| 4 | Completar RNF-09 (al menos una prueba por regla de negocio) y el dashboard completo | Semana 5 |
| 5 | Manual y guía rápida (RF-21) y funciones *Should* si hay tiempo | Semana 6 |
| 6 | **Piloto** en al menos 3 talleres (2 formales y 1 informal): medir el proceso en papel, capacitar, usar el sistema y aplicar el cuestionario de usabilidad | Semana 7 en adelante |
| 7 | Ajustar los capítulos 4 y 7 de la tesis con los datos reales del piloto (H-3) | Después del piloto |

Ver el [documento de Trabajo futuro](09-trabajo-futuro.md).

## 9. Conclusión

El proyecto pasó de una investigación diagnóstica a un **prototipo funcional, probado y documentado**, que cubre el flujo operativo completo de un taller y cumple la protección de datos personales que exige la ley colombiana. La decisión más importante del diseño fue **registrar cada evento con fecha, hora y usuario**: eso convierte al sistema en el instrumento con el que el piloto podrá responder, con datos y no con percepciones, la pregunta de investigación.
